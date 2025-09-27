from typing import List
import cv2
import matplotlib.pyplot as plt
import numpy as np
from facenet_pytorch import MTCNN
from emotiefflib.facial_analysis import EmotiEffLibRecognizer, get_model_list
def recognize_faces(frame: np.ndarray, device: str) -> List[np.ndarray]:
    def detect_face(frame: np.ndarray):
        mtcnn = MTCNN(keep_all=False, post_process=False, min_face_size=40, device=device)
        bounding_boxes, probs = mtcnn.detect(frame, landmarks=False)
        if probs[0] is None:
            return []
        bounding_boxes = bounding_boxes[probs > 0.9]
        return bounding_boxes

    bounding_boxes = detect_face(frame)
    facial_images = []
    for bbox in bounding_boxes:
        box = bbox.astype(int)
        x1, y1, x2, y2 = box[0:4]
        facial_images.append(frame[y1:y2, x1:x2, :])
    return facial_images
def emotion_from_array(frame:np.ndarray):
    emotion_class = ['분노','경멸','혐오','두려움','행복','보통','슬픔','놀람']
    device = "cpu"
    model_name = get_model_list()[0]
    facial_images = recognize_faces(frame, device)
    fer = EmotiEffLibRecognizer(engine="onnx", model_name=model_name, device=device)
    emotions = []
    for face_img in facial_images:
        emotion, test = fer.predict_emotions(face_img, logits=True)
        emotions.append(test[0].tolist())
        # print(emotion,test)
    return softmax(emotions[0]), emotion_class
    
def emotion_from_file(image_path:str):
    # emotion_class = ['분노','경멸','혐오','두려움','행복','보통','슬픔','놀람']
    # device = "cpu"
    # model_name = get_model_list()[0]
    frame_bgr = cv2.imread(image_path)
    frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    return emotion_from_array(frame)
    # facial_images = recognize_faces(frame, device)
    # fer = EmotiEffLibRecognizer(engine="onnx", model_name=model_name, device=device)
    # emotions = []
    # for face_img in facial_images:
    #     emotion, test = fer.predict_emotions(face_img, logits=True)
    #     emotions.append(test[0].tolist())
    #     # print(emotion,test)
    # return emotions, emotion_class
def softmax(lst):
    min_val = min(lst)
    max_val = max(lst)
    if max_val == min_val:
        return [0.0 for _ in lst]  # 모든 값이 같을 경우 0으로 처리
    return [(x - min_val) / (max_val - min_val) for x in lst]
def argmax(lst:list):
    _max = max(lst)
    for idx, d in enumerate(lst):
        if d == _max:
            return idx