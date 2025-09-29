from fastapi import WebSocket
from copy import deepcopy
from enum import Enum
from lib.game_manager import GameStage

class ChatCode(Enum):
    SUCCESS='200'       ## 프로세스 성공 메시지
    GAME_WAIT='201'     ## 게임 1명만 접속된 상태
    GAME_READY='202'    ## 게임 스테이지 준비 메시지
    GAME_ON='203'       ## 게임 스테이지 준비 메시지
    GAME_END='204'      ## 게임 스테이지 완료 메시지
    ERROR='400'         ## 오류
    SYSTEM='100'        ## 시스템 알림
    
class ChatMessage:
    def __init__(self) -> None:
        self.chat_message = {
            ChatCode.SUCCESS : 'SUCCESS',
            ChatCode.GAME_WAIT : 'WAIT',
            ChatCode.GAME_READY : 'READY',
            ChatCode.GAME_ON : 'ON',
            ChatCode.GAME_END : 'DONE',
            ChatCode.ERROR : 'ERROR',
            ChatCode.SYSTEM : 'SYSTEM'
        }
    
    def message(self,code:ChatCode,message:str|None=None,stage=None):
        if stage is None:
            stage = {
                'result':[],
                'stage':[]
            }
        return {
            'code':code.value,
            'status': self.chat_message[code],
            'message':message if message else '',
            'info':stage,
        }

class ConnectionManager:
    def __init__(self):
        ## 접속 가능 멤버 수
        self.MAX_PERSON = 2
        self.GAME_READY = False
        self.GAME_ON = False
        self.room: dict[str,list[str]] = {
            'active':[],
            'wait':[]
        }
        self.game_stage:dict[str,GameStage] = {}
        self.connection_pool: dict[str,WebSocket] = {}
        # self.wait_connections: dict[str,WebSocket] = {}
        self.chat_message = ChatMessage()

    def make_game(self,room:str):
        self.game_stage[room] = GameStage(self.room[room],2)
        ## 게임 스테이지 만들고 현재 스테이지 전송
    
    async def connect(self, id:str, websocket: WebSocket):
        await websocket.accept()
        self.connection_pool[id] = websocket
        print(self.GAME_READY)
        if self.GAME_READY:
        ## game 시작 상태, 게임 접속 2명 완료된 상태임
            self.room['wait'].append(id)
            await self.send_message(id,ChatCode.SYSTEM,'게임중입니다. 다음에 다시 시도하세요.')
        else:
        ## game 시작전 상태
            self.room['active'].append(id)
            ## 메시지 보내기
            if len(self.room['active']) == 2:
                ## 게임 상태 완료
                self.GAME_READY = True
                ## active 방에 메시지 보내기 : 게임 시작 준비 완료 메시지
                msg = self.chat_message.message(ChatCode.GAME_READY,'게임을 시작할 준비가 되었습니다')
                await self.broadcast('active',ChatCode.GAME_READY,'게임을 시작할 준비가 되었습니다')
                if self.GAME_ON == False:
                    ## 게임 스테이지 생성 하고 게임 진행
                    self.make_game('active')
                    ## 스테이지 정보 전송
                    # stage = next(self.game_stage['active'])
                    # print(stage)
                    await self.game_start('active',ChatCode.GAME_ON)
                    self.GAME_ON = True
            else:
                ## 게임 추가 구성원 기다리
                self.GAME_READY = False
                ## active 방에 메시지 보내기 : 게임 대기중 메시지
                msg = self.chat_message.message(ChatCode.GAME_WAIT,'게임을 시작하려면 두사람이 필요합니다. 조금만 기다려 주세요.')
                await websocket.send_json(msg)

    async def disconnect(self, id:str):
        ## 제거전 메시지?
        ## room에서 제거
        if id in self.room['active']:
            self.room['active'].remove(id)
            self.GAME_READY = False
            ## 룸 상태 변경시 처리??
        elif id in self.room['wait']:
            self.room['wait'].remove(id)
        ## pool에서 제거
        websocket = self.connection_pool.pop(id, None)
        if websocket:
            try:
                await websocket.close()
            except:
                print(f'{id} :: 소켓 close중 에러 발생')

    ## 특정 아이디에게 보내기
    async def send_message(self,receive_id:str, code:ChatCode, message: str):
        websocket = self.connection_pool[receive_id]
        if websocket:
            msg = self.chat_message.message(code,message)
            await websocket.send_json(msg)

    async def send_personal_message(self, sender_id: str, receiver_id: str, message: str):
        await self.send_message(receiver_id, f"[{sender_id}] {message}")

    ## 특정룸에 메시지 보내기
    async def broadcast(self,room:str,code:ChatCode,message:str):
        msg = self.chat_message.message(code,message)
        for id in self.room[room]:
            await self.connection_pool[id].send_json(msg)
            
    ## 게임 시작 정보 메시지 보내기
    async def game_start(self,room:str,code:ChatCode):
        stage = next(self.game_stage['active'])
        game_info={
            'stage':stage
        }
        print(stage)
        msg = self.chat_message.message(code,f'시작 - 라운드 {stage[0]} : {stage[1]}',game_info)
        for id in self.room[room]:
            await self.connection_pool[id].send_json(msg)

    ## 게임 진행 정보 메시지 보내기
    async def game_process(self,room:str,code:ChatCode):
        stage = next(self.game_stage['active'])
        self.game_stage['active'].get_results()
        print(stage)
        game_info = {
            'stage':stage,
            'result':self.game_stage['active'].get_results(),
            'ids':self.room['active'],
        }
        msg = self.chat_message.message(code,f'진행 - 라운드 {stage[0]} : {stage[1]}',game_info)
        for id in self.room[room]:
            await self.connection_pool[id].send_json(msg)
