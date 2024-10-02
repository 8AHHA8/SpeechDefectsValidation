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

    
mp_face_mesh = mp.solutions.face_mesh
face_mesh_detector = mp_face_mesh.FaceMesh(max_num_faces=1)

def smile():
    print("Smile detection started")
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, img = cap.read()
        if not ret:
            break
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        mouths = mouth_cascade.detectMultiScale(
            gray,
            scaleFactor=1.7,
            minNeighbors=22,
            minSize=(25, 25),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        smile_detected = False
        for (sx, sy, sw, sh) in mouths:
            aspect_ratio = sw / sh
            if aspect_ratio > 1.7 and sy > img.shape[0] // 2:
                smile_detected = True
                center = (sx + sw // 2, sy + sh // 2)
                axes = (sw // 2, sh // 2)
                cv2.ellipse(img, center, axes, 0, 0, 360, (0, 255, 0), 2)
        
        results = face_mesh_detector.process(img_rgb)
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = img.shape

            upper_lip_id = 13
            lower_lip_id = 14
            left_corner_id = 61
            right_corner_id = 291

            upper_lip_y = int(landmarks[upper_lip_id].y * h)
            lower_lip_y = int(landmarks[lower_lip_id].y * h)
            left_corner_x = int(landmarks[left_corner_id].x * w)
            left_corner_y = int(landmarks[left_corner_id].y * h)
            right_corner_x = int(landmarks[right_corner_id].x * w)
            right_corner_y = int(landmarks[right_corner_id].y * h)

            corner_distance = np.sqrt((right_corner_x - left_corner_x) ** 2 + (right_corner_y - left_corner_y) ** 2)

            cv2.line(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), (int(landmarks[lower_lip_id].x * w), lower_lip_y), (255, 0, 0), 2)

            if lower_lip_y - upper_lip_y > 10:
                mouth_status = 'Mouth Open'
            else:
                mouth_status = 'Mouth Closed'

            if corner_distance > 70:
                smile_detected = True
                smile_text = 'Smiling'
            else:
                smile_text = 'Not Smiling'

            cv2.circle(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (int(landmarks[lower_lip_id].x * w), lower_lip_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (left_corner_x, left_corner_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (right_corner_x, right_corner_y), 5, (0, 255, 0), -1)

            cv2.line(img, (left_corner_x, left_corner_y), (right_corner_x, right_corner_y), (255, 0, 0), 2)

            cv2.putText(img, f'Distance: {corner_distance:.2f}', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        else:
            mouth_status = 'Mouth Status Unavailable'
            smile_text = 'Not Smiling'

        cv2.putText(img, smile_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, mouth_status, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)
        
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        app.update()
                
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()
pass
    