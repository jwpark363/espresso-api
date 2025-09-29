# Face 분석을 통한 표정 연기 대결 게임
- 프론트 : 언리얼
- 백앤드 : FastApi, WebSocket
- 모델 : ‘Efficient Emotion Analysis and Facial Expression Recognition’
- 모델 링크 : https://github.com/sb-ai-lab/EmotiEffLib

### 시나리오
1. 익명의 두사람이 서버 접속
2. 게임방이 생성되고 표정 대결 스테이지 생성(제시어 전송)
3. 각자 제시어에 맞는 표정을 지어 해당 사진을 서버 전송
4. 전송된 사진을 모델을 통해 분석
5. 분석 결과
    - 1. 해당 사진의 표정 분류, 제시어에 대한 score, 사진
    - 2. 상대방의 표정 분류, 제시어에 대한 score, 사진
    - 3. 다음 스테이지 제시어
6. 분석 결과를 자신의 것과 상대방의 것을 비교하여 보여줌