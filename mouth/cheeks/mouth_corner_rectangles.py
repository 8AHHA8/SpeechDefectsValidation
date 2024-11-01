def get_mouth_corner_rectangles(landmarks, w, h):
    left_mouth_corner = landmarks[61]
    right_mouth_corner = landmarks[291]

    left_x, left_y = int(left_mouth_corner.x * w), int(left_mouth_corner.y * h)
    right_x, right_y = int(right_mouth_corner.x * w), int(right_mouth_corner.y * h)

    left_rect_top_left = (left_x - 80, left_y - 80)
    left_rect_bottom_right = (left_x, left_y + 40)

    right_rect_top_left = (right_x, right_y - 80)
    right_rect_bottom_right = (right_x + 80, right_y + 40)

    return (left_rect_top_left, left_rect_bottom_right), (right_rect_top_left, right_rect_bottom_right)
