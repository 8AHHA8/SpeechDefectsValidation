import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

def get_extended_lower_face_coordinates(landmarks, img_width, img_height):
    nose_tip = landmarks[1]
    chin = landmarks[152]

    nose_x, nose_y = int(nose_tip.x * img_width), int(nose_tip.y * img_height)
    chin_x, chin_y = int(chin.x * img_width), int(chin.y * img_height)

    top_left = (nose_x - 70, nose_y)
    bottom_right = (chin_x + 70, chin_y + 10)

    return top_left, bottom_right