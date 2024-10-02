import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

def get_extended_lower_face_coordinates(landmarks, img_width, img_height):
    """Get the extended lower face rectangle coordinates."""
    nose_tip = landmarks[1]
    chin = landmarks[152]

    # Convert normalized coordinates to pixel coordinates
    nose_x, nose_y = int(nose_tip.x * img_width), int(nose_tip.y * img_height)
    chin_x, chin_y = int(chin.x * img_width), int(chin.y * img_height)

    # Define rectangle coordinates
    top_left = (nose_x - 70, nose_y)  # Increased width around the nose
    bottom_right = (chin_x + 70, chin_y + 10)  # Increased width below the chin

    return top_left, bottom_right

def draw_optical_flow_vectors(frame, flow, top_left, bottom_right):
    """Draw optical flow vectors inside the given rectangle."""
    sum_fx = 0
    sum_fy = 0
    count = 0
    
    for y in range(top_left[1], bottom_right[1], 10):  # Adjust step for density of vectors
        for x in range(top_left[0], bottom_right[0], 10):
            fx, fy = flow[y, x]
            cv2.arrowedLine(frame, (x, y), (int(x + fx), int(y + fy)), (255, 0, 0), 1, tipLength=0.3)
            sum_fx += fx
            sum_fy += fy
            count += 1

    return sum_fx, sum_fy, count

def determine_directions(avg_fx, avg_fy, horizontal_threshold, vertical_threshold):
    """Determine horizontal and vertical direction based on average flow."""
    horizontal_direction = None
    vertical_direction = None

    # Determine horizontal direction
    if abs(avg_fx) > horizontal_threshold:
        horizontal_direction = "Tongue Pointing Right" if avg_fx > 0 else "Tongue Pointing Left"

    # Determine vertical direction
    if abs(avg_fy) > vertical_threshold:
        vertical_direction = "Tongue Pointing Down" if avg_fy > 0 else "Tongue Pointing Up"

    return horizontal_direction, vertical_direction

def display_directions(frame, horizontal_direction, vertical_direction):
    """Display the current horizontal and vertical direction messages."""
    if horizontal_direction is not None:
        cv2.putText(frame, horizontal_direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    if vertical_direction is not None:
        cv2.putText(frame, vertical_direction, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def tongue():
    cap = cv2.VideoCapture(0)
    prev_gray = None

    vertical_movement_threshold = 1
    horizontal_movement_threshold = 0.1

    current_horizontal_direction = None
    current_vertical_direction = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
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
                top_left, bottom_right = get_extended_lower_face_coordinates(face_landmarks.landmark, img_width, img_height)
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

                sum_fx, sum_fy, count = draw_optical_flow_vectors(frame, flow, top_left, bottom_right)

                if count > 0:
                    avg_fx = sum_fx / count
                    avg_fy = sum_fy / count

                    new_horizontal_direction, new_vertical_direction = determine_directions(avg_fx, avg_fy, horizontal_movement_threshold, vertical_movement_threshold)

                    # Update directions
                    if new_horizontal_direction and new_horizontal_direction != current_horizontal_direction:
                        current_horizontal_direction = new_horizontal_direction
                    if new_vertical_direction and new_vertical_direction != current_vertical_direction:
                        current_vertical_direction = new_vertical_direction

        # Display directions
        display_directions(frame, current_horizontal_direction, current_vertical_direction)

        # Update previous frame
        prev_gray = gray
        cv2.imshow('Extended Lower Face Detection with Optical Flow', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
