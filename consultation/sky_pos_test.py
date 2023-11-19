import math

def get_position(time):

    x = 1.5 - time / 12
    if 6 <= time <= 18:
        y = math.sqrt(math.pow(0.5, 2) - math.pow((x-0.5), 2)) + 0.5
    else:
        y = -100

    return (x, y)


print(get_position(3))