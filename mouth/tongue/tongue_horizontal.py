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

def tongue_horizontal():
    print("Horizontal Tongue detection started")
    
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
    horizontal_movement_threshold = 1

    current_horizontal_direction = None
    
    left_count = 0
    right_count = 0

    prev_time = time.time()

    try:
        while camera_active:
            ret, frame = cap.read()
            if not ret:
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
                    top_left, bottom_right = get_extended_lower_face_coordinates(face_landmarks.landmark, w, h)
                    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                    sum_fx, sum_fy, count = draw_optical_flow_vectors(frame, flow, top_left, bottom_right)

                    if count > 0:
                        avg_fx = sum_fx / count
                        avg_fy = sum_fy / count

                        new_horizontal_direction, _ = determine_directions(avg_fx, avg_fy, horizontal_movement_threshold, 2)

                        if new_horizontal_direction and new_horizontal_direction != current_horizontal_direction:
                            current_horizontal_direction = new_horizontal_direction
                            if current_horizontal_direction == "Tongue Pointing Left":
                                right_count += 1
                            elif current_horizontal_direction == "Tongue Pointing Right":
                                left_count += 1

                cv2.putText(frame, f'Left: {left_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                cv2.putText(frame, f'Right: {right_count}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            display_directions(frame, current_horizontal_direction, None)

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

    except Exception as e:
        print(f"An error occurred during camera processing: {e}")
    finally:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
