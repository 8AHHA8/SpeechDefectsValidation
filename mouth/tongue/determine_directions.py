import cv2
import numpy as np
import mediapipe as mp


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