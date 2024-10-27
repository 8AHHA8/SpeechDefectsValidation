import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np
from display import app, camera_canvas

face_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_frontalface_alt2.xml')
mouth_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_smile.xml')

mp_face_mesh = mp.solutions.face_mesh
face_mesh_detector = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def kiss():
    print("Kiss detection started")
    
    cap = cv2.VideoCapture(0)
    kiss_count = 0
    kiss_detected = False  # Initial kiss status
    
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

            # New condition for excessive distance
            if corner_distance > 55:
                text = 'Too far'
                kiss_detected = False  # Reset kiss status to allow new detection later
            elif corner_distance < 50:
                text = 'Kiss Detected'
                if not kiss_detected:
                    kiss_count += 1  # Increment only when kiss status changes to "detected"
                    kiss_detected = True
            else:
                text = 'No Kiss'
                kiss_detected = False  # Reset when kiss is no longer detected

            # Visual indicators
            cv2.circle(img, (left_corner_x, left_corner_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (right_corner_x, right_corner_y), 5, (0, 255, 0), -1)
            cv2.line(img, (left_corner_x, left_corner_y), (right_corner_x, right_corner_y), (255, 0, 0), 2)
            
            # Display distance, kiss detection, kiss count, and excessive distance alert
            cv2.putText(img, f'Distance: {corner_distance:.2f}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Kiss Count: {kiss_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
        
        # Update Tkinter canvas
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)
        
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        app.update()
                
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        
    cap.release()
    cv2.destroyAllWindows()
