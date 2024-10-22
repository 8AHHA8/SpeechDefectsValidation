import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from display import app, camera_canvas
import time 
from .determine_puffed import determine_puffed
from .mouth_corner_rectangles import get_mouth_corner_rectangles
from .optical_flow_vectors import draw_optical_flow_vectors
from .puffed_status import display_puffed_status

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

def cheeks():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    prev_gray = None
    prev_time = cv2.getTickCount()

    puff_threshold = 5
    current_puffed_status = None
    puffed_time = 0
    freeze_duration = 3

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is None:
            prev_gray = gray
            continue

        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        img_height, img_width, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                (left_top_left, left_bottom_right), (right_top_left, right_bottom_right) = get_mouth_corner_rectangles(face_landmarks.landmark, img_width, img_height)

                cv2.rectangle(frame, left_top_left, left_bottom_right, (0, 255, 0), 2)
                cv2.rectangle(frame, right_top_left, right_bottom_right, (0, 255, 0), 2)

                sum_fx_left, _ = draw_optical_flow_vectors(frame, flow, left_top_left, left_bottom_right)
                sum_fx_right, _ = draw_optical_flow_vectors(frame, flow, right_top_left, right_bottom_right)

                new_puffed_status = determine_puffed(sum_fx_left, sum_fx_right, puff_threshold)

                if new_puffed_status == "Puffed":
                    if current_puffed_status != "Puffed":
                        current_puffed_status = "Puffed"
                        puffed_time = time.time()
                elif new_puffed_status == "Not puffed":
                    if current_puffed_status == "Puffed":
                        if (time.time() - puffed_time) > freeze_duration:
                            current_puffed_status = "Not puffed"

        elapsed_time = time.time() - puffed_time
        timer_text = f'Timer: {int(elapsed_time)}s' if current_puffed_status == "Puffed" else ''

        display_puffed_status(frame, current_puffed_status, timer_text)

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
