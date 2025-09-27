import os, uvicorn, json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from routers.face_landmark import router as face_landmark_router
from lib.connection_manager import ConnectionManager

app = FastAPI(title="Expresso Bot API", vision="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

manager = ConnectionManager()
app.include_router(face_landmark_router)

@app.get("/")
def home():
    return RedirectResponse(url="/index.html")

@app.get("/chat")
def chat():
    return RedirectResponse(url="/chat.html")

@app.websocket("/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print(user_id)
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            receiver_id = data["to"]
            message = data["message"]
            await manager.send_personal_message(user_id, receiver_id, message)
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.websocket("/face_landmark")
async def websocket_text(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        print(data)
        response_list  = ["안녕","반가워","[END]"]
        for word in response_list:
            await websocket.send_text(word)
        await websocket.send_text('[END]')
        # response=chat_bot(data['question'],'')
        # # print(response)
        # for chunk in response:
        #     chunk_text = chunk.choices[0].delta.content
        #     print(chunk_text,end='')
        #     if chunk_text is None:
        #         print('')
        #         continue
        #     await websocket.send_text(chunk_text)
        # await websocket.send_text("[END]")
    except Exception as e:
        print(f"Websocket 에러 발생: {e}")
    finally:
        await websocket.close()
        print("Websocket 연결 종료")



print('static folder......')
# static 등록
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static"), name="static")
print('ready to service......')
if __name__ == "__main__":
    # Render는 PORT 환경변수를 제공
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
