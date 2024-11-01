import cv2
from PIL import Image, ImageTk  # Importuj PIL do obsługi formatów obrazów w Tkinterze
import mediapipe as mp
from display import app, camera_canvas
from .lower_face_coordinates import get_extended_lower_face_coordinates  # Importuj funkcję do uzyskiwania współrzędnych dolnej części twarzy
from .optical_flow_vectors import draw_optical_flow_vectors  # Importuj funkcję do obliczania wektorów przepływu optycznego
from .determine_directions import determine_directions  # Importuj funkcję do określania kierunków ruchu
from .display_directions import display_directions  # Importuj funkcję do wyświetlania kierunków ruchu
import time  # Importuj moduł time do mierzenia liczby klatek na sekundę (FPS)

mp_face_mesh = mp.solutions.face_mesh # Inicjalizacja detektora siatki twarzy MediaPipe
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)  # Wykrywaj maksymalnie jedną twarz

def tongue():
    print("Tongue detection started")

    cap = cv2.VideoCapture(0)  # Uruchamia kamerę (0 oznacza domyślne urządzenie wideo)

    prev_gray = None  # Inicjalizuj zmienną do przechowywania poprzedniej klatki w skali szarości dla przepływu optycznego
    vertical_movement_threshold = 0.5  # Próg czułości dla ruchu pionowego
    horizontal_movement_threshold = 0.1  # Próg czułości dla ruchu poziomego

    current_horizontal_direction = None  # Zmienna do przechowywania aktualnie wykrywanego kierunku poziomego
    current_vertical_direction = None  # Zmienna do przechowywania aktualnie wykrywanego kierunku pionowego
    
    up_count = 0
    down_count = 0
    left_count = 0
    right_count = 0

    prev_time = time.time()  # Zapisz początkowy czas do mierzenia liczby klatek na sekundę (FPS)

    while True:  # Główna pętla przechwytywania klatek i przetwarzania wykrywania języka
        ret, frame = cap.read()  # Odczytaj bieżącą klatkę z kamery
        if not ret:
            print("Error: Could not read frame.")  # Wypisz błąd, jeśli klatka nie mogła zostać odczytana
            break  # Zakończ pętlę, jeśli odczytanie klatki się nie powiedzie

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Przekształć bieżącą klatkę na skalę szarości do przepływu optycznego
        if prev_gray is None:  # Jeśli to jest pierwsza klatka
            prev_gray = gray  # Ustaw bieżącą klatkę w skali szarości jako poprzednią
            continue  # Pomiń resztę pętli dla pierwszej klatki

        # Oblicz przepływ optyczny między poprzednią a bieżącą klatką w skali szarości wykorzystując funkcję Gunnara Farnbacka
        # prev_gray - poprzednia klatka przetwarzana w skali szarości
        # gray - bierząca klatka przetwarzana w skali szarości
        # None - stworzenie nowego miejsca na zapisanie wyników
        # 0.5 - skala piramidy ustawiona na 50% oznacza, że będą próbkowane w dół(downsampling) o połowę swojego rozmiaru wraz z każdym poziomem piramidy 
        # 3 - określenie liczby poziomów piramidy
        # 10 - rozmiar okna o wymiarze 15 na 15 pikseli, które będzie służyło do określania wektorów ruchu dla każdej pikseli
        # 10 - liczba iteracji(określenie ile razy algorytm będzie poprawiał swoje szacowanie ruchu na każdym poziomie piramidy/rozmytego obrazu)
        # 5 - parametr określający jak duży obszar wokół każdego piksela będzie brany pod uwagę do analizy(sprawdzanie czy sąsiadujące ze sobą piksele poruszają się razem)
        # 1.2 -  wartość określająca intensywność poziomu wygładzania obrazu
        # 0 - parametr  odpowiedzialny za ustawienie dodatkowych opcji(niewykorzystany)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 10, 10, 5, 1.2, 0)
        
        # Pobieranie wysokości i szerokości obrazu
        h, w, _ = frame.shape
        
        # Przekształcanie klatki na RGB do przetwarzania przez MediaPipe
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Wykrycie punktów charakterystycznych twarzy przy użyciu MediaPipe
        results = face_mesh.process(img_rgb)

        if results.multi_face_landmarks:  # Jeśli wykryto punkty charakterystyczne
            for face_landmarks in results.multi_face_landmarks:  # Przejdź przez każdą wykrytą twarz
                # Uzyskaj współrzędne rozszerzonego obszaru dolnej części twarzy (w tym ust)
                top_left, bottom_right = get_extended_lower_face_coordinates(face_landmarks.landmark, w, h)

                # Narysuj prostokąt wokół obszaru dolnej części twarzy
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

                # Oblicz sumę wektorów przepływu optycznego w obszarze dolnej części twarzy
                sum_fx, sum_fy, count = draw_optical_flow_vectors(frame, flow, top_left, bottom_right)

                if count > 0:  # Jeśli znaleziono wektory przepływu optycznego w regionie
                    avg_fx = sum_fx / count  # Oblicz średni poziomy wektor przepływu
                    avg_fy = sum_fy / count  # Oblicz średni pionowy wektor przepływu

                    # Określ nowe kierunki ruchu na podstawie średnich wektorów przepływu
                    new_horizontal_direction, new_vertical_direction = determine_directions(avg_fx, avg_fy, horizontal_movement_threshold, vertical_movement_threshold)

                     # Jeśli zmienił się kierunek poziomy, zaktualizuj go
                    if new_horizontal_direction and new_horizontal_direction != current_horizontal_direction:
                        current_horizontal_direction = new_horizontal_direction
                        if current_horizontal_direction == "Tongue Pointing Right":
                            right_count += 1
                        elif current_horizontal_direction == "Tongue Pointing Left":
                            left_count += 1

                    # Jeśli zmienił się kierunek pionowy, zaktualizuj go
                    if new_vertical_direction and new_vertical_direction != current_vertical_direction:
                        current_vertical_direction = new_vertical_direction
                        if current_vertical_direction == "Tongue Pointing Up":
                            up_count += 1
                        elif current_vertical_direction == "Tongue Pointing Down":
                            down_count += 1

            # Wyświetlanie liczników na klatce
            cv2.putText(frame, f'Up: {up_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f'Down: {down_count}', (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f'Left: {left_count}', (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame, f'Right: {right_count}', (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)


        # Wyświetl wykryte kierunki ruchu na klatce
        display_directions(frame, current_horizontal_direction, current_vertical_direction)

        # Ustaw bieżącą klatkę w skali szarości jako poprzednią do następnej iteracji pętli
        prev_gray = gray

        # Zmierz czas między klatkami, aby obliczyć liczbę klatek na sekundę (FPS)
        current_time = cv2.getTickCount()
        time_diff = (current_time - prev_time) / cv2.getTickFrequency()  # Oblicz różnicę czasową
        fps = 1.0 / time_diff  # Oblicz liczbę klatek na sekundę
        prev_time = current_time  # Zaktualizuj poprzedni czas do następnej klatki

        # Wyświetl liczbę FPS na klatce
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Przekształć klatkę na obraz PIL do wyświetlania w Tkinterze
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Przekształć obraz PIL na format, który może wyświetlić Tkinter
        tk_img = ImageTk.PhotoImage(image=pil_img)

        # Zaktualizuj canvas kamery nowym obrazem
        camera_canvas.create_image(0, 0, anchor="nw", image=tk_img)
        camera_canvas.image = tk_img  # Przechowuj obraz, aby zapobiec jego usunięciu przez garbage collector

        # Odśwież aplikację Tkinter, aby pokazać zaktualizowaną klatkę
        app.update()

    # Zwolnij kamerę wideo i zamknij wszystkie okna OpenCV po zakończeniu pętli
    cap.release()
    cv2.destroyAllWindows()
