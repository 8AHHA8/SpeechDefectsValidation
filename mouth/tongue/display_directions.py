import cv2

def display_directions(frame, horizontal_direction, vertical_direction):  # Definiuje funkcję do wyświetlania kierunków ruchu na klatce wideo
    if horizontal_direction is not None:  # Jeśli wykryto kierunek poziomy (nie jest pusty)
        # Wyświetla tekst z kierunkiem poziomym na obrazie w pozycji (10, 30) z czcionką Hershey Simplex, rozmiarem 0.7 i kolorem białym (255, 255, 255)
        cv2.putText(frame, horizontal_direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    if vertical_direction is not None:  # Jeśli wykryto kierunek pionowy (nie jest pusty)
        # Wyświetla tekst z kierunkiem pionowym na obrazie w pozycji (10, 90) z czcionką Hershey Simplex, rozmiarem 0.7 i kolorem białym (255, 255, 255)
        cv2.putText(frame, vertical_direction, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
