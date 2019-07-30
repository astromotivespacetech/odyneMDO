def normalize(val, min, max):

    if val - min == 0:
        return 0
    else:
        normalized = (val - min) / (max - min)
        return normalized


def constrain(val, min, max):

    if val > max:
        val = max
    elif val < min:
        val = min

    return val


def constrain_normalized(val, min, max):

    n = normalize(val, min, max)
    v = constrain(n, 0.0, 1.0)

    return v



def tabs(num):

    str = ""
    for _ in range(num):
        str += "\t"
    return str
