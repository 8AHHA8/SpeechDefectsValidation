import cv2

def draw_optical_flow_vectors(frame, flow, top_left, bottom_right):  # Definiuje funkcję do rysowania wektorów przepływu optycznego w danym obszarze
    sum_fx = 0  # Inicjalizuje sumę wartości wektorów poziomych (ruch w poziomie) jako 0
    sum_fy = 0  # Inicjalizuje sumę wartości wektorów pionowych (ruch w pionie) jako 0
    count = 0   # Inicjalizuje licznik do śledzenia liczby wektorów przepływu optycznego
    
    # Przechodzi przez każdy punkt w obszarze między górnym lewym a dolnym prawym rogiem, z krokiem 10 pikseli w pionie
    for y in range(top_left[1], bottom_right[1], 10): 
        # Przechodzi przez każdy punkt w poziomie w obszarze między górnym lewym a dolnym prawym rogiem, z krokiem 10 pikseli w poziomie
        for x in range(top_left[0], bottom_right[0], 10):
            fx, fy = flow[y, x]  # Pobiera wektory przepływu optycznego dla piksela (x, y) - fx (poziomy), fy (pionowy)
            
            # Rysuje "strzałkę" (wektor przepływu) na obrazie, wskazującą kierunek ruchu w danym punkcie
            cv2.arrowedLine(frame, (x, y), (int(x + fx), int(y + fy)), (255, 0, 0), 1, tipLength=0.3)
            
            sum_fx += fx  # Dodaje poziomy wektor ruchu do sumy poziomych wektorów
            sum_fy += fy  # Dodaje pionowy wektor ruchu do sumy pionowych wektorów
            count += 1    # Zwiększa licznik wektorów, które zostały przetworzone

    # Zwraca sumę poziomych i pionowych wektorów ruchu oraz liczbę przetworzonych punktów
    return sum_fx, sum_fy, count
