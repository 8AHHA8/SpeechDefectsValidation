import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np
from display import app, camera_canvas
from .lower_face_coordinates import get_extended_lower_face_coordinates
from .optical_flow_vectors import draw_optical_flow_vectors
from .determine_directions import determine_directions
from .display_directions import display_directions

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

def tongue():
    print("Tongue detection started")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    prev_gray = None
    vertical_movement_threshold = 1
    horizontal_movement_threshold = 0.1

    current_horizontal_direction = None
    current_vertical_direction = None

    instruction_start_time = cv2.getTickCount()
    instruction_duration = 10 * cv2.getTickFrequency()

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

        if (cv2.getTickCount() - instruction_start_time) < instruction_duration:
            instruction_text = "Please adjust yourself!"
            cv2.putText(frame, instruction_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        else:
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    top_left, bottom_right = get_extended_lower_face_coordinates(face_landmarks.landmark, img_width, img_height)
                    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

                    sum_fx, sum_fy, count = draw_optical_flow_vectors(frame, flow, top_left, bottom_right)

                    if count > 0:
                        avg_fx = sum_fx / count
                        avg_fy = sum_fy / count

                        new_horizontal_direction, new_vertical_direction = determine_directions(avg_fx, avg_fy, horizontal_movement_threshold, vertical_movement_threshold)

                        if new_horizontal_direction and new_horizontal_direction != current_horizontal_direction:
                            current_horizontal_direction = new_horizontal_direction
                        if new_vertical_direction and new_vertical_direction != current_vertical_direction:
                            current_vertical_direction = new_vertical_direction

            display_directions(frame, current_horizontal_direction, current_vertical_direction)

        prev_gray = gray

        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)

        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        camera_canvas.image = tk_img 

        app.update() 

    cap.release()
    cv2.destroyAllWindows()
pass