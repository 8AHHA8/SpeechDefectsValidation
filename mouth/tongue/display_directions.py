import cv2

def display_directions(frame, horizontal_direction, vertical_direction):
    if horizontal_direction is not None:
        cv2.putText(frame, horizontal_direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    if vertical_direction is not None:
        cv2.putText(frame, vertical_direction, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)