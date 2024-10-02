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

def kiss():
    print("Kiss detection started")
    
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
            
            left_corner_id = 61
            right_corner_id = 291

            left_corner_x = int(landmarks[left_corner_id].x * w)
            left_corner_y = int(landmarks[left_corner_id].y * h)
            right_corner_x = int(landmarks[right_corner_id].x * w)
            right_corner_y = int(landmarks[right_corner_id].y * h)

            corner_distance = np.sqrt((right_corner_x - left_corner_x) ** 2 + (right_corner_y - left_corner_y) ** 2)

            if corner_distance < 50:
                text = 'Kiss Detected'
            else:
                text = 'No Kiss'

            cv2.circle(img, (left_corner_x, left_corner_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (right_corner_x, right_corner_y), 5, (0, 255, 0), -1)
            
            cv2.line(img, (left_corner_x, left_corner_y), (right_corner_x, right_corner_y), (255, 0, 0), 2)
            
            cv2.putText(img, f'Distance: {corner_distance:.2f}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)
        
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        app.update()
                
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()
pass

