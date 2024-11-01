def get_left_mouth_corner_rectangle(landmarks, w, h):
    left_mouth_corner = landmarks[291]

    left_x, left_y = int(left_mouth_corner.x * w), int(left_mouth_corner.y * h)

    left_rect_top_left = (left_x, left_y - 80)
    left_rect_bottom_right = (left_x + 80, left_y + 40)

    return left_rect_top_left, left_rect_bottom_right
