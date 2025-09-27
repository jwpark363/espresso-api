import sys
import cv2
import mediapipe as mp

### mediapipe Face Landmark
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh 

face_detection = mp_face_detection.FaceDetection(
    model_selection = 0,  # 0: 근거리, 1: 원거리
    min_detection_confidence=0.5
)
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=2,
    min_detection_confidence=0.5,
    refine_landmarks=True
)

## CV Vide Cam
vcap = cv2.VideoCapture(0)

while True:
    ret, frame = vcap.read()
    if not ret:
        print('camera does not working!')
        sys.exit()
    # flip left right
    frame = cv2.flip(frame, 1)
    
    '''
    #### Face Landmark Process ####
    frame.flags.writeable = True
    results = face_detection.process(frame)
    # print(results.multi_hand_landmarks)

    ## draw face mark 전체 그리기
    if results.detections:
        for detection in results.detections:
            mp_drawing.draw_detection(frame, detection)
    ################################
    #### Face Mesh Landmark Process ####
    frame.flags.writeable = True
    results = face_mesh.process(frame)
    # print(results.multi_hand_landmarks)
    height, width, _ = frame.shape
    ## draw face mark 원하는 부분만
    if results.multi_face_landmarks:
        targets = [468,473] ## 눈 중앙
        for landmarks in results.multi_face_landmarks:
            # mp_drawing.draw_landmarks(
            #     frame,
            #     landmarks,
            #     mp_face_mesh.FACEMESH_TESSELATION,
            #     mp_drawing.DrawingSpec(
            #         color=(0,255,0),
            #         thickness=1,
            #         circle_radius=1
            #     )
            # )
            for idx in targets: 
                landmark = landmarks.landmark[idx]
                cv2.circle(
                    frame,
                    (int(landmark.x*width),int(landmark.y*height)),
                     5,
                     (0,0,255),
                     1
                )
            break
    ################################
    '''
    
    ### 입술간 거리
    frame.flags.writeable = True
    results = face_mesh.process(frame)
    height, width, _ = frame.shape
    ## draw face mark 원하는 부분만
    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            landmark = landmarks.landmark
            target_up = landmark[13] #위입술
            target_down = landmark[14] #아래입술
            up_x, up_y = int(target_up.x * width), int(target_up.y * height)
            down_x, down_y = int(target_down.x * width), int(target_down.y * height)        
            cv2.circle(frame, (up_x,up_y), 5, (0,0,255),2)
            cv2.circle(frame, (down_x,down_y), 5, (0,255,0),2)
            cv2.line(frame, (up_x,up_y),(down_x,down_y), (255,0,0),3)
            ### 입술간 거리
            distance = ((up_x - down_x)**2 + (up_y-down_y)**2)**0.5
            print(f'distance : f{distance}')
    
    # show
    cv2.imshow('webcam', frame)
    # exit when press ESC key
    key = cv2.waitKey(1)
    if key == 27:
        break
    
vcap.release()
cv2.destroyAllWindows()
    