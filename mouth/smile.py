import cv2  # Import biblioteki OpenCV do przetwarzania obrazów
from PIL import Image, ImageTk  # Import modułów do konwersji obrazów na formaty obsługiwane przez Tkinter
import mediapipe as mp  # Import MediaPipe, narzędzia do analizy twarzy
import numpy as np  # Import NumPy do operacji matematycznych na tablicach
from display import app, camera_canvas  # Import elementów GUI z pliku display (aplikacja i obszar rysowania)

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

def smile():
    print("Smile detection started")

    cap = cv2.VideoCapture(0)  # Uruchamia kamerę (0 oznacza domyślne urządzenie wideo)
    
    open_mouth_smiles = 0
    closed_mouth_smiles = 0
    smile_detected = False

    while True:  # Pętla, która będzie działać, dopóki nie zostanie przerwana
        ret, img = cap.read()  # Odczyt klatki z kamery
        if not ret:  # Jeśli nie udało się odczytać klatki, przerwij pętlę
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Konwertuje obraz z BGR (OpenCV) na RGB (MediaPipe)

        results = face_mesh_detector.process(img_rgb)  # Wykrywa punkty charakterystyczne twarzy za pomocą MediaPipe
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

            # Oblicza odległość między kącikami ust
            corner_distance = np.sqrt((right_corner_x - left_corner_x) ** 2 + (right_corner_y - left_corner_y) ** 2)

            # Rysuje linię między górną a dolną wargą
            cv2.line(img, (int(landmarks[upper_lip_id].x * w), upper_lip_y), (int(landmarks[lower_lip_id].x * w), lower_lip_y), (255, 0, 0), 2)
            
            if lower_lip_y - upper_lip_y > 10:
                mouth_status = 'Mouth Open'
                mouth_open = True
            else:
                mouth_status = 'Mouth Closed'
                mouth_open = False

            if corner_distance > 70:
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

        # Konwertuje obraz z OpenCV na format obsługiwany przez Tkinter
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # Konwersja BGR -> RGB, a następnie na obraz PIL
        tk_img = ImageTk.PhotoImage(image=pil_img)  # Konwersja na obraz Tkinter

        # Rysuje obraz w oknie aplikacji
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)  # Umieszcza obraz w lewym górnym rogu
        app.update()  # Aktualizuje GUI

        # Wyjście z pętli po naciśnięciu klawisza 'q'
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    # Zamyka kamerę i okna OpenCV
    cap.release()  # Zwalnia zasoby kamery
    cv2.destroyAllWindows()  # Zamyka wszystkie okna OpenCV
pass