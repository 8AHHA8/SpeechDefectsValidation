import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np
from display import app, camera_canvas


face_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_frontalface_alt2.xml')
eye_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_eye.xml')
mouth_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_smile.xml')
nose_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_mcs_nose.xml')

face_mesh_detector = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def mouth_closed_open():
    print("mouth status button pressed")
    
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        if not ret:
            break
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh_detector.process(img_rgb)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = img.shape

            upper_lip_id = 13
            lower_lip_id = 14

            upper_lip_y = int(landmarks[upper_lip_id].y * h)
            lower_lip_y = int(landmarks[lower_lip_id].y * h)

            lip_distance = lower_lip_y - upper_lip_y

            cv2.line(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), (int(landmarks[lower_lip_id].x * w), lower_lip_y), (255, 0, 0), 2)

            if lip_distance > 20:
                mouth_text = 'Mouth Open'
            else:
                mouth_text = 'Mouth Closed'

            cv2.circle(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (int(landmarks[lower_lip_id].x * w), lower_lip_y), 5, (0, 255, 0), -1)
            
            cv2.putText(img, f'Distance: {lip_distance:.2f}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        else:
            mouth_text = 'Mouth closed'
           
        cv2.putText(img, mouth_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)
        
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        app.update()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows() 
pass    