import machine
import ssd1306
import time
import math
import random
import helpers

i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

x = 0
y = 0
prevX = 0
prevY = 0

while True:
    # R = random.randint(26, 45)
    # r = random.randint(15, R)
    # d = random.randint(1, 50)
    R = 50
    r = 35
    d = 20

    dt = 0.05
    maxT = 2 * math.pi * r / helpers.gcd(R, r)
    theta = 0

    oled.fill(0)
    oled.show()

    while theta < maxT:
        while (x == prevX) and (y == prevY):
            x = int((R - r) * math.cos(theta) + d * math.cos((R - r) * theta / r))
            y = int((R - r) * math.sin(theta) - d * math.sin((R - r) * theta / r))
            theta = theta + dt

        oled.pixel(x + 64, y + 32, 1)
        oled.show()
        prevX = x
        prevY = y

    time.sleep(2)


