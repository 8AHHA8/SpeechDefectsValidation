import cv2

def draw_optical_flow_vectors(frame, flow, top_left, bottom_right):
    sum_fx = 0
    count = 0

    top_y, bottom_y = top_left[1], bottom_right[1]
    left_x, right_x = top_left[0], bottom_right[0]

    for y in range(top_y, bottom_y, 10):
        for x in range(left_x, right_x, 10):
            if 0 <= y < flow.shape[0] and 0 <= x < flow.shape[1]:
                fx, _ = flow[y, x]
                cv2.arrowedLine(frame, (x, y), (int(x + fx), y), (255, 0, 0), 1, tipLength=0.3)
                sum_fx += fx
                count += 1

    return sum_fx, count