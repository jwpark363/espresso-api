import os, uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from lib.connection_manager import ConnectionManager, ChatCode

app = FastAPI(title="Expresso Bot API", vision="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

manager = ConnectionManager()

@app.get("/")
def chat():
    return RedirectResponse(url="/chat.html")

@app.websocket("/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(f'connection socket {user_id}')
    await manager.connect(user_id, websocket)
    try:
        while True:
            ## 게임 모드 일때 파일 내용을 받음
            data = await websocket.receive_json()
            if manager.GAME_READY and manager.GAME_ON:
                ## 데이터 받아 분석
                print(f'{user_id}{"-"*60}')
                # print(data)
                image = data['image']
                # print(image)
                result = manager.game_stage['active'].image_to_emotion(user_id,image)
                await manager.game_process('active',ChatCode.GAME_ON)
                # print(result)
                print(f'{user_id}{"-"*60}')
            # receiver_id = data["to"]
            # message = data["message"]
            # await manager.send_personal_message(user_id, receiver_id, message)
    except WebSocketDisconnect:
        manager.disconnect(user_id)

print('static folder......')
# static 등록
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static"), name="static")
print('ready to service......')
if __name__ == "__main__":
    # Render는 PORT 환경변수를 제공
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
