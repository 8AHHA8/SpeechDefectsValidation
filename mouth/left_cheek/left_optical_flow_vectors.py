import cv2

def draw_optical_flow_vectors(frame, flow, top_left, bottom_right):
    sum_fx = 0
    count = 0

    left_y, right_y = top_left[1], bottom_right[1]
    right_x, left_x = top_left[0], bottom_right[0]

    for y in range(left_y, right_y, 10):
        for x in range(right_x, left_x, 10):
            if 0 <= y < flow.shape[0] and 0 <= x < flow.shape[1]:
                fx, _ = flow[y, x]
                cv2.arrowedLine(frame, (x, y), (int(x + fx), y), (255, 0, 0), 1, tipLength=0.3)
                sum_fx += fx
                count += 1

    return sum_fx, count
