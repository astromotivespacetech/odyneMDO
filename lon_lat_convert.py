


def convert(deg, min, sec):

    return deg + min/60 + sec/3600



if __name__ == "__main__":
    
    # x = convert(57, 26, 05.935)
    x = convert(152, 20, 30.117)
    print(x)
