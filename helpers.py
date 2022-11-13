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
