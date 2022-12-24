import math

# least common multiple
def gcd(a, b):
    if a % b == 0:
        return b
    if b % a == 0:
        return a
    if a > b:
        return gcd(a % b, b)
    return gcd(a, b % a)


# greatest common divisor
def lcm(a, b):
    return a * b / gcd(a, b)

def scale_value(value, in_min, in_max, out_min, out_max):
  scaled_value = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  return math.ceil(scaled_value)

class RemoteData(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
