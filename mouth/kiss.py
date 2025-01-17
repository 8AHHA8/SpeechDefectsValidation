import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np
from display import app, camera_canvas, camera_active, cap

face_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_frontalface_alt2.xml')
mouth_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_smile.xml')

face_mesh_detector = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def on_close():
    print("Closing window...")
    global camera_active, cap
    
    if cap is not None:
        cap.release()
        cap = None
    
    camera_active = False
    camera_canvas.delete("all")
    app.destroy()

def kiss():
    print("Kiss detection started")

    global camera_active, cap

    if camera_active:
        print("Stopping the camera...")
        camera_active = False
        cap.release()
        camera_canvas.delete("all")
        return

    print("Starting the camera...")
    camera_active = True
    cap = cv2.VideoCapture(0)
    
    kiss_count = 0
    kiss_detected = False
    
    def update_frame():
        nonlocal kiss_count, kiss_detected

        if not camera_active:
            return

        ret, img = cap.read()
        if not ret:
            camera_canvas.delete("all")
            return

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh_detector.process(img_rgb)

        app.protocol("WM_DELETE_WINDOW", on_close)
            
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

            if corner_distance > 70:
                text = 'Too close to the screen'
                kiss_detected = False
            elif corner_distance < 50:
                text = 'Kiss Detected'
                if not kiss_detected:
                    kiss_count += 1
                    kiss_detected = True
            else:
                text = 'No Kiss'
                kiss_detected = False

            cv2.circle(img, (left_corner_x, left_corner_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (right_corner_x, right_corner_y), 5, (0, 255, 0), -1)
            cv2.line(img, (left_corner_x, left_corner_y), (right_corner_x, right_corner_y), (255, 0, 0), 2)
            cv2.putText(img, f'Distance: {corner_distance:.2f}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Kiss Count: {kiss_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
        else:
            cv2.putText(img, 'No face detected', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)

        camera_canvas.image = tk_img
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)

        if camera_active:
            app.after(1, update_frame)

    app.protocol("WM_DELETE_WINDOW", on_close)
    update_frame()
