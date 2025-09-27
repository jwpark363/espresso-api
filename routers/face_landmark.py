import cv2,uuid,os
import numpy as np
from fastapi import APIRouter, UploadFile, File
from lib.landmark_util import face_landmark_from_rgbimage, make_landmark_image
from lib.errors import Error, ErrorInfo

router = APIRouter()
print('*** face landmark router')


def create_error_response(filename, code, message):
    return {
        "filename": filename,
        "code": code,
        "status": "error",
        "message": message
    }

@router.post('/landmark')
async def face_landmark(file: UploadFile = File(...)):
    print(':::::: face landmark...')
    print(file)
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)      # NumPy 배열
    img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # 이미지로 디코딩
    response = None
    save_path = './static/download'
    if file.filename is None:
        response = ErrorInfo.create_error_response(
                'None',
                Error.FILE_NOT_FOUND
        )
    elif img_cv is None:
        response = ErrorInfo.create_error_response(
                file.filename,
                Error.DECODE_FAILED
        )
    else:        
        # 파일 저장명 생성
        ext = file.filename.split(".")[-1]
        file_id = uuid.uuid4().hex[:9]
        file_name = f"{file_id}.{ext}"
        landmark_name = f"{file_id}_landmark.{ext}"
        file_path = os.path.join(save_path,file_name)
        landmark_path = os.path.join(save_path,landmark_name)
        rgb_image = cv2.cvtColor(img_cv,cv2.COLOR_BGR2RGB)
        # 이미지 저장
        cv2.imwrite(file_path, img_cv)
        landmark_image = make_landmark_image(rgb_image)
        print(landmark_path)
        cv2.imwrite(landmark_path, cv2.cvtColor(landmark_image,cv2.COLOR_RGB2BGR))
        landmark = face_landmark_from_rgbimage(rgb_image)
        response = {
            "source_image": file.filename,
            "landmark_image":landmark_name,
            "code": Error.SUCCESS_CODE,
            "result": landmark
        }
    return response