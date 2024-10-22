def determine_puffed(sum_fx_left, sum_fx_right, puff_threshold):
    if sum_fx_left < -puff_threshold and sum_fx_right > puff_threshold:
        return "Puffed"
    elif sum_fx_left > -puff_threshold and sum_fx_right < puff_threshold:
        return "Not puffed"
    else:
        return None