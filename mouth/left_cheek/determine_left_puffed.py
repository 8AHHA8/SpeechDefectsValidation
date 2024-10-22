def determine_puffed(sum_fx_left, puff_threshold):
    if sum_fx_left > puff_threshold:
        return "Left Cheek Movement"
    else:
        return "No Movement"
