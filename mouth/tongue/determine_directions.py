def determine_directions(avg_fx, avg_fy, horizontal_threshold, vertical_threshold):  # Definiuje funkcję, która określa kierunki ruchu na podstawie średnich wektorów przepływu
    horizontal_direction = None  # Inicjalizuje zmienną do przechowywania kierunku poziomego jako None
    vertical_direction = None  # Inicjalizuje zmienną do przechowywania kierunku pionowego jako None

    # Sprawdza, czy wartość absolutna średniego wektora poziomego jest większa od progu
    if abs(avg_fx) > horizontal_threshold:
        # Ustala kierunek ruchu poziomego: w prawo, jeśli avg_fx jest dodatnie, w lewo, jeśli ujemne
        horizontal_direction = "Tongue Pointing Right" if avg_fx > 0 else "Tongue Pointing Left"

    # Sprawdza, czy wartość absolutna średniego wektora pionowego jest większa od progu
    if abs(avg_fy) > vertical_threshold:
        # Ustala kierunek ruchu pionowego: w dół, jeśli avg_fy jest dodatnie, w górę, jeśli ujemne
        vertical_direction = "Tongue Pointing Down" if avg_fy > 0 else "Tongue Pointing Up"

    # Zwraca wykryte kierunki poziomy i pionowy (możliwe, że są None, jeśli nie wykryto ruchu)
    return horizontal_direction, vertical_direction
