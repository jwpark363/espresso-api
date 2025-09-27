# Controller
from fastapi import APIRouter, UploadFile, File, Form
from app.data.sql_util import read_sql

router = APIRouter()
print(':::read all member api')

############################
# 이미지파일 리스트
############################
@router.get("/members")
async def all_member():
    print(f"members start ::::::::::::::::::")
    members = read_sql('select * from member')
    return members.to_dict(orient='records')

