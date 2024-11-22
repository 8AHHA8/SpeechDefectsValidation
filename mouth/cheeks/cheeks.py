import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from display import app, camera_canvas, camera_active, cap
import time 
from .determine_puffed import determine_puffed
from .mouth_corner_rectangles import get_mouth_corner_rectangles
from .optical_flow_vectors import draw_optical_flow_vectors
from .puffed_status import display_puffed_status

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

def on_close():
    print("Closing window...")
    global camera_active, cap
    camera_active = False

    if cap is not None:
        cap.release()

    camera_canvas.delete("all")
    app.destroy()

def cheeks():

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
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    prev_gray = None
    prev_time = cv2.getTickCount()

    puff_threshold = 5
    current_puffed_status = None
    puffed_time = 0
    freeze_duration = 3
    puff_count = 0

    def update_frame():
        nonlocal puff_threshold, current_puffed_status, prev_time, prev_gray, puffed_time, freeze_duration, puff_count

        if not camera_active:
            return

        ret, frame = cap.read()
        if not ret:
            camera_canvas.delete("all")
            return
            
        app.protocol("WM_DELETE_WINDOW", on_close)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is None:
            prev_gray = gray
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            tk_img = ImageTk.PhotoImage(image=pil_img)
            camera_canvas.image = tk_img
            camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
            app.after(1, update_frame)
            return

        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 10, 10, 5, 1.2, 0)
            
        h, w, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                (left_top_left, left_bottom_right), (right_top_left, right_bottom_right) = get_mouth_corner_rectangles(face_landmarks.landmark, w, h)

                cv2.rectangle(frame, left_top_left, left_bottom_right, (0, 255, 0), 2)
                cv2.rectangle(frame, right_top_left, right_bottom_right, (0, 255, 0), 2)

                sum_fx_left, _ = draw_optical_flow_vectors(frame, flow, left_top_left, left_bottom_right)
                sum_fx_right, _ = draw_optical_flow_vectors(frame, flow, right_top_left, right_bottom_right)

                new_puffed_status = determine_puffed(sum_fx_left, sum_fx_right, puff_threshold)

                if new_puffed_status == "Puffed":
                    if current_puffed_status != "Puffed":
                        current_puffed_status = "Puffed"
                        puffed_time = time.time()
                        puff_count += 1
                elif new_puffed_status == "Not puffed":
                    if current_puffed_status == "Puffed":
                        if (time.time() - puffed_time) > freeze_duration:
                            current_puffed_status = "Not puffed"

        elapsed_time = time.time() - puffed_time
        timer_text = f'Timer: {int(elapsed_time)}s' if current_puffed_status == "Puffed" else ''

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

        camera_canvas.image = tk_img
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)

        if camera_active:
            app.after(1, update_frame)

    app.protocol("WM_DELETE_WINDOW", on_close)
    update_frame()
