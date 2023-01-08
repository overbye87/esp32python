from machine import Pin, PWM, I2C
from time import sleep_ms
import json

import helpers
from esp32ble import ESP32_BLE, led
from dcmotor import DCMotor
import ssd1306

i2c = I2C(scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)
oled.show()

frequency = 15000
m_left_enable = PWM(Pin(14), freq=frequency)
m_left_pin1 = Pin(26, Pin.OUT)
m_left_pin2 = Pin(27, Pin.OUT)
m_right_enable = PWM(Pin(25), freq=frequency)
m_right_pin1 = Pin(33, Pin.OUT)
m_right_pin2 = Pin(32, Pin.OUT)
dc_motor_left = DCMotor(m_left_pin1, m_left_pin2, m_left_enable, 0, 1023)
dc_motor_right = DCMotor(m_right_pin1, m_right_pin2, m_right_enable, 0, 1023)

# ble_msg = ''

# but = Pin(0, Pin.IN)
oled.text('awaiting', 24 + 8, 20)
oled.text('bluetooth', 24 + 4, 30)
oled.text('connection', 24, 40)
oled.show()
ble = ESP32_BLE("ESP32BLE")

prev_ble_msg = ''

# def buttons_irq(pin):
#     led.value(not led.value())
#     # ble.send('LED state will be toggled.')
#     print('LED state will be toggled.')
#
#
# but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)


def set_motors_speed(var_l, var_r):
    oled.fill(0)
    oled.line(43, 28, 43, helpers.scale_value(var_l, -100, 100, 56, 0), 1)
    oled.line(85, 28, 85, helpers.scale_value(var_r, -100, 100, 56, 0), 1)
    oled.text(str(var_l), 43-8, 56)
    oled.text(str(var_r), 85-8, 56)
    oled.show()
    if var_l > 0:
        dc_motor_left.forward(abs(var_l))
    elif var_l < 0:
        dc_motor_left.backwards(abs(var_l))
    else:
        dc_motor_left.stop()

    if var_r > 0:
        dc_motor_right.forward(abs(var_r))
    elif var_r < 0:
        dc_motor_right.backwards(abs(var_r))
    else:
        dc_motor_right.stop()

while True:
    ble_msg = ble.ble_msg
    if (bool(ble_msg) and ble_msg != prev_ble_msg):
        json_object = json.loads(ble_msg)
        remote_data = helpers.RemoteData(**json_object)
        print(ble_msg)
        var_l = remote_data.l
        var_r = remote_data.r
        set_motors_speed(var_l, var_r)  # ←←← MOTORS
        prev_ble_msg = ble_msg
        ble_msg = ''
    sleep_ms(50)


