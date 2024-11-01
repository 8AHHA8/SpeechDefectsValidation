import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from display import app, camera_canvas
import time
from .determine_right_puffed import determine_puffed
from .right_mouth_corner_rectangle import get_right_mouth_corner_rectangle
from .right_optical_flow_vectors import draw_optical_flow_vectors 
from .right_puffed_status import display_puffed_status


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

def right_cheek():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    prev_gray = None
    prev_time = cv2.getTickCount()

    puff_threshold = 15
    current_puffed_status = None
    puffed_time = 0
    freeze_duration = 3
    puff_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is None:
            prev_gray = gray
            continue

        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 10, 10, 5, 1.2, 0)
        
        h, w, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                right_top_left, right_bottom_right = get_right_mouth_corner_rectangle(face_landmarks.landmark, w, h)

                cv2.rectangle(frame, right_top_left, right_bottom_right, (0, 255, 0), 2)

                sum_fx_left, _ = draw_optical_flow_vectors(frame, flow, right_top_left, right_bottom_right)

                new_puffed_status = determine_puffed(sum_fx_left, puff_threshold)

                if new_puffed_status == "Right Cheek Movement":
                    if current_puffed_status != "Right Cheek Movement":
                        current_puffed_status = "Right Cheek Movement"
                        puffed_time = time.time()
                        puff_count += 1
                elif new_puffed_status == "No Movement":
                    if current_puffed_status == "Right Cheek Movement":
                        if (time.time() - puffed_time) > freeze_duration:
                            current_puffed_status = "No Movement"

        elapsed_time = time.time() - puffed_time
        timer_text = f'Timer: {int(elapsed_time)}s' if current_puffed_status == "Right Cheek Movement" else ''

        display_puffed_status(frame, current_puffed_status, timer_text)
        
        cv2.putText(frame, f'Puffs Detected: {puff_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        prev_gray = gray

        current_time = cv2.getTickCount()
        time_diff = (current_time - prev_time) / cv2.getTickFrequency()
        fps = 1.0 / time_diff
        prev_time = current_time

        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)

        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        camera_canvas.image = tk_img 

        app.update() 

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
