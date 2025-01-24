import cv2  # Import biblioteki OpenCV do przetwarzania obrazów
from PIL import Image, ImageTk  # Import modułów do konwersji obrazów na formaty obsługiwane przez Tkinter
import mediapipe as mp  # Import MediaPipe, narzędzia do analizy twarzy
import numpy as np  # Import NumPy do operacji matematycznych na tablicach
from display import app, camera_canvas, camera_active, cap  # Import elementów GUI z pliku display (aplikacja i obszar rysowania)

# Ładowanie klasyfikatorów Haar do wykrywania cech twarzy
face_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_frontalface_alt2.xml')  # Klasyfikator do wykrywania twarzy
mouth_cascade = cv2.CascadeClassifier('.\opencv\data\haarcascades\haarcascade_smile.xml')  # Klasyfikator do wykrywania uśmiechu

# Inicjalizacja detektora siatki twarzy MediaPipe
face_mesh_detector = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,  # Maksymalna liczba twarzy do wykrycia
    min_detection_confidence=0.5,  # Minimalna pewność detekcji
    min_tracking_confidence=0.5  # Minimalna pewność śledzenia
)

mp_face_mesh = mp.solutions.face_mesh  # Skrócona nazwa do odwoływania się do modułu FaceMesh
face_mesh_detector = mp_face_mesh.FaceMesh(max_num_faces=1)  # Detektor do wykrywania jednej twarzy

def on_close():
    print("Closing window...")
    global camera_active, cap
    camera_active = False

    if cap is not None:
        cap.release()

    camera_canvas.delete("all")
    app.destroy()

def smile():
    print("Smile detection started")

    global camera_active, cap

    if camera_active:
        print("Stopping the camera...")
        camera_active = False
        cap.release()
        camera_canvas.delete("all")
        return

    print("Starting the camera...")
    camera_active = True
    cap = cv2.VideoCapture(0)
    
    open_mouth_smiles = 0
    closed_mouth_smiles = 0
    smile_detected = False

    def update_frame():
        nonlocal open_mouth_smiles, closed_mouth_smiles, smile_detected

        if not camera_active:
            return

        ret, img = cap.read()
        if not ret:
            camera_canvas.delete("all")
            return

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Konwertuje obraz z BGR (OpenCV) na RGB (MediaPipe)
        results = face_mesh_detector.process(img_rgb)  # Wykrywa punkty charakterystyczne twarzy za pomocą MediaPipe

        app.protocol("WM_DELETE_WINDOW", on_close)
            
        if results.multi_face_landmarks:  # Jeśli wykryto punkty charakterystyczne
            landmarks = results.multi_face_landmarks[0].landmark  # Pobiera punkty charakterystyczne pierwszej twarzy
            h, w, _ = img.shape  # Pobiera wysokość, szerokość i liczbę kanałów obrazu

            # Indeksy punktów charakterystycznych dla ust i kącików ust
            upper_lip_id = 13  # Number indeksu górnej wargi
            lower_lip_id = 14  # Number indeksu dolnej wargi
            left_corner_id = 61  # Number indeksu lewego kącika ust
            right_corner_id = 291  # Number indeksu prawego kącika ust

            # Przekształcanie współrzędnych znormalizowanych na piksele
            upper_lip_y = int(landmarks[upper_lip_id].y * h)  # Y górnej wargi
            lower_lip_y = int(landmarks[lower_lip_id].y * h)  # Y dolnej wargi
            left_corner_x = int(landmarks[left_corner_id].x * w)  # X lewego kącika ust
            left_corner_y = int(landmarks[left_corner_id].y * h)  # Y lewego kącika ust
            right_corner_x = int(landmarks[right_corner_id].x * w)  # X prawego kącika ust
            right_corner_y = int(landmarks[right_corner_id].y * h)  # Y prawego kącika ust
                
            # Oblicza odległość między wargami
            lip_distance = lower_lip_y - upper_lip_y
                
            # Oblicza odległość między kącikami ust
            corner_distance = np.sqrt((right_corner_x - left_corner_x) ** 2 + (right_corner_y - left_corner_y) ** 2)

            if lip_distance > 10:
                mouth_status = 'Mouth Open'
                mouth_open = True
            else:
                mouth_status = 'Mouth Closed'
                mouth_open = False

            if corner_distance > 80:
                smile_text = 'Smiling'
                if not smile_detected:
                    if mouth_open:
                        open_mouth_smiles += 1
                    else:
                        closed_mouth_smiles += 1
                    smile_detected = True
            else:
                smile_text = 'Not Smiling'
                smile_detected = False

                    
            # Rysuje linię między górną a dolną wargą
            cv2.line(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), (int(landmarks[lower_lip_id].x * w), lower_lip_y), (255, 0, 0), 2)

            # Rysuje kółka wokół ust i kącików
            cv2.circle(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), 5, (0, 255, 0), -1)  # Górna warga
            cv2.circle(img, (int(landmarks[lower_lip_id].x * w), lower_lip_y), 5, (0, 255, 0), -1)  # Dolna warga
            cv2.circle(img, (left_corner_x, left_corner_y), 5, (0, 255, 0), -1)  # Lewy kącik ust
            cv2.circle(img, (right_corner_x, right_corner_y), 5, (0, 255, 0), -1)  # Prawy kącik ust

            # Rysuje linię między kącikami ust
            cv2.line(img, (left_corner_x, left_corner_y), (right_corner_x, right_corner_y), (255, 0, 0), 2)

            # Wyświetla status uśmiechu i ust na obrazie
            cv2.putText(img, smile_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, mouth_status, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Distance: {corner_distance:.2f}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Smiles open: {open_mouth_smiles}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, f'Smiles closed: {closed_mouth_smiles}', (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2, cv2.LINE_AA)
        else:
            mouth_status = 'Mouth Status Unavailable'  # Brak danych o ustach
            smile_text = 'Not Smiling'  # Brak uśmiechu

        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        tk_img = ImageTk.PhotoImage(image=pil_img)

        camera_canvas.image = tk_img
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)

        if camera_active:
            app.after(1, update_frame)

    app.protocol("WM_DELETE_WINDOW", on_close)
    update_frame()
        
