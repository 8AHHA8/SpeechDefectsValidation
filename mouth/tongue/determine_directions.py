def determine_directions(avg_fx, avg_fy, horizontal_threshold, vertical_threshold):
    horizontal_direction = None
    vertical_direction = None

    if abs(avg_fx) > horizontal_threshold:
        horizontal_direction = "Tongue Pointing Right" if avg_fx > 0 else "Tongue Pointing Left"

    if abs(avg_fy) > vertical_threshold:
        vertical_direction = "Tongue Pointing Down" if avg_fy > 0 else "Tongue Pointing Up"

    return horizontal_direction, vertical_direction