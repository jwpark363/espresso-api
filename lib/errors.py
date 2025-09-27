# ERROR 정리
from enum import Enum

class Error(Enum):
    SUCCESS_CODE = "E000"
    DECODE_FAILED = "E001"
    FACE_NOT_FOUND = "E002"
    FILE_NOT_FOUND = "E003"
    UNKNOWN_ERROR = "E999"

class ErrorInfo:
    MESSAGE = {
        Error.DECODE_FAILED : "이미지를 디코딩할 수 없습니다.",
        Error.FACE_NOT_FOUND : "얼굴 감지를 실패했습니다.",
        Error.FILE_NOT_FOUND : "파일을 찾을 수 없습니다.",
        # 'DB_INSERT_FAILED' : "DB 입력을 실패했습니다.",
        # 'INVALID_MODE' : "유효하지 않은 모드입니다.",
        # 'NAME_NOT_FOUND' : "이름을 찾을 수 없습니다.",
        # 'ID_NOT_FOUND' : "ID 인식을 실패했습니다.",
        Error.UNKNOWN_ERROR : "알 수 없는 에러입니다.",
    }
    @staticmethod
    def create_error_response(filename:str, code:Error):
        return {
            "filename": filename,
            "code": code,
            "status": "error",
            "message": ErrorInfo.MESSAGE[code],
        }