import cv2
from PIL import Image, ImageTk
import mediapipe as mp
from display import app, camera_canvas, camera_active, cap
from .lower_face_coordinates import get_extended_lower_face_coordinates
from .optical_flow_vectors import draw_optical_flow_vectors
from .determine_directions import determine_directions
from .display_directions import display_directions
import time

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

def tongue_vertical():
    print("Vertical Tongue detection started")
    
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

    prev_gray = None
    vertical_movement_threshold = 2

    current_vertical_direction = None
    
    up_count = 0
    down_count = 0

    prev_time = time.time()

    def update_frame():
        nonlocal up_count, down_count, prev_time, prev_gray, current_vertical_direction, vertical_movement_threshold

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
                top_left, bottom_right = get_extended_lower_face_coordinates(face_landmarks.landmark, w, h)
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                sum_fx, sum_fy, count = draw_optical_flow_vectors(frame, flow, top_left, bottom_right)

                if count > 0:
                    avg_fx = sum_fx / count
                    avg_fy = sum_fy / count

                    _, new_vertical_direction = determine_directions(avg_fx, avg_fy, 1, vertical_movement_threshold)

                    if new_vertical_direction and new_vertical_direction != current_vertical_direction:
                        current_vertical_direction = new_vertical_direction
                        if current_vertical_direction == "Tongue Pointing Up":
                            up_count += 1
                        elif current_vertical_direction == "Tongue Pointing Down":
                            down_count += 1

            cv2.putText(frame, f'Up: {up_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f'Down: {down_count}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        display_directions(frame, None, current_vertical_direction)

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
