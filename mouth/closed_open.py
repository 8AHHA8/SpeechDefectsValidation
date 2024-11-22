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

def closed_open():
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

    open_count = 0
    close_count = 0
    mouth_status = 'closed'

    def update_frame():
        nonlocal open_count, close_count, mouth_status

        if not camera_active:
            return

        ret, img = cap.read()
        if not ret:
            camera_canvas.delete("all")
            return

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

            if lip_distance > 20:
                current_status = 'open'
            else:
                current_status = 'closed'

            if current_status != mouth_status:
                if current_status == 'open':
                    open_count += 1
                else:
                    close_count += 1
                mouth_status = current_status

            cv2.line(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), (int(landmarks[lower_lip_id].x * w), lower_lip_y), (255, 0, 0), 2)
            cv2.circle(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), 5, (0, 255, 0), -1)
            cv2.circle(img, (int(landmarks[lower_lip_id].x * w), lower_lip_y), 5, (0, 255, 0), -1)
            cv2.putText(img, f'Mouth: {current_status.capitalize()}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Distance: {lip_distance:.2f}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Opens: {open_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Closes: {close_count}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
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
