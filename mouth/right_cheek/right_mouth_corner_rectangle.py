def get_right_mouth_corner_rectangle(landmarks, img_width, img_height):
    right_mouth_corner = landmarks[61]

    right_x, right_y = int(right_mouth_corner.x * img_width), int(right_mouth_corner.y * img_height)

    right_rect_top_left = (right_x - 80, right_y - 80)
    right_rect_bottom_right = (right_x, right_y + 40)

    return right_rect_top_left, right_rect_bottom_right
