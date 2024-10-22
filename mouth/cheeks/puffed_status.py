import cv2

def display_puffed_status(frame, puffed_status, timer_text):
    if puffed_status:
        cv2.putText(frame, puffed_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, timer_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
