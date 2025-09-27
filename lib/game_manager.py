import random, base64, cv2
import numpy as np
from PIL import Image
from io import BytesIO
from lib.emotiefflib import emotion_from_array, softmax, argmax

GAME_EMOTIONS = ['분노','경멸','혐오','두려움','행복','보통','슬픔','놀람']

class GameStage:
    def __init__(self,ids:list[str], step=3) -> None:
        game_stage = GAME_EMOTIONS.copy()
        random.shuffle(game_stage)
        self.stage = game_stage[:step]
        self.current_step = -1
        self.next_step = 0
        self.ids = ids
        ## 각 스테이지 결과 저장
        self.results = {}
        for stage in range(step):
            self.results[str(stage)] = {}
            for id in self.ids:
                self.results[str(stage)][id] = {}
    
    def __iter__(self):
        return self
        # for step,stage in enumerate(self.stage):
        #     yield step+1,stage
    def __next__(self):
        ## 현재 스텝 -1 OR 현재 스텝의 모든 아이디의 결과가 저장 되었다면 다음스템으로
        ## 그렇지 않다면 움ㅇ지이지 않음
        if self.current_step == -1 or self.check_currentstage():
            self.current_step = self.next_step
            if self.current_step >= len(self.stage):
                raise StopIteration
            self.next_step = self.next_step + 1
        return self.current_step, self.stage[self.current_step]
    
    def image_to_emotion(self,id:str,base64_string:str):
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        image_np = np.array(image)
        result = emotion_from_array(image_np)
        self.results[str(self.current_step)][id] = {
            'image':base64_string,
            'result':result
        }
        self.print()
        return result
    def get_results(self):
        return self.results
    ##현재 스템의 평가가 끝이 났는지 여부 체크
    def check_currentstage(self):
        for id in self.ids:
            if self.results[str(self.current_step)][id].get('result',None) is None:
                return False
        return True
    
    def print(self):
        for stage in self.results:
            print(f'{"="*10} {stage}')
            for id in self.ids:
                print(f'{"-"*10} {id}')
                print(self.results[stage][id].get('result','진행전'))