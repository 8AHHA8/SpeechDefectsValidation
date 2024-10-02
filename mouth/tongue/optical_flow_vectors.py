import cv2
import numpy as np
import mediapipe as mp


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