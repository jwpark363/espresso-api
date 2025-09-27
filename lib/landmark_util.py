import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
model_path = './datasets/models/face_landmarker.task'#'face_landmarker_v2_with_blendshapes.task'
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(base_options=base_options,
                                       output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True,
                                       num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

'''
Extract Face Landmark Infomation From Image File
image_file_path : Image File Path
is_normal : normalize 상태의 값 여부
'''
def face_landmark_from_file(image_file_path:str, is_normal=False):
    img = cv2.imread("./datasets/images/business-person.png")
    height,width,_ = img.shape
    if is_normal:
        height = 1
        width = 1
    mp_image = mp.Image.create_from_file(image_file_path)
    results = detector.detect(mp_image)
    face_landmarks = results.face_landmarks[0]
    face_blendshapes = results.face_blendshapes[0]
    return {
        'landmark':[{'id':idx, 'x':int(landmark.x*width), 'y':int(landmark.y*height)}
                  for idx,landmark in enumerate(face_landmarks)],
        'score':[{'id':face.index,'score':face.score,'name':face.category_name}
                  for face in sorted(face_blendshapes, key=lambda x: x.score, reverse=True)[:3]],
        'category':[face.category_name for face in face_blendshapes]
    }
'''
Extract Face Landmark Infomation From RGB Image Data
np_image : RGB Numpy Image Data
is_normal : normalize 상태의 값 여부
'''
def face_landmark_from_rgbimage(np_image:np.ndarray, is_normal=False):
    height,width,_ = np_image.shape
    if is_normal:
        height = 1
        width = 1
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_image)    
    results = detector.detect(mp_image)
    face_landmarks = results.face_landmarks[0]
    face_blendshapes = results.face_blendshapes[0]
    return {
        'landmark':[{'id':idx, 'x':int(landmark.x*width), 'y':int(landmark.y*height)}
                  for idx,landmark in enumerate(face_landmarks)],
        'score':[{'id':face.index,'score':face.score,'name':face.category_name}
                  for face in sorted(face_blendshapes, key=lambda x: x.score, reverse=True)[:3]],
        'category':[face.category_name for face in face_blendshapes]
    }
'''
Make Landmark Image From BGR Image Data(cv image)
np_image : RGB Numpy Image Data
'''
def make_landmark_image(np_image:np.ndarray):
    image = np_image.copy()
    result = face_landmark_from_rgbimage(np_image)
    points = result['landmark']
    for point in points:
        cv2.circle(image,[point['x'],point['y']],1,(255,0,0),1)
    return image