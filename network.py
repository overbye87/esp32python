import network
import socket
import machine
import dht

import ssd1306

i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

import json
import time

ssid = 'overbye_main'
password = '1234567890'

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>ESP32</title>
    </head>
    <body>
        <h1>Hi from ESP32</h1>
    </body>
</html>
"""


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        oled.fill(0)
        oled.text('Connecting to Wi-Fi...', 20, 20)
        oled.show()
        print('Connecting to Wi-Fi...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass

    oled.fill(0)
    oled.text(sta_if.ifconfig(), 20, 20)
    oled.show()
    print('Network config:', sta_if.ifconfig())


do_connect()
addr = socket.getaddrinfo('', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)
d = dht.DHT11(machine.Pin(15))
d.measure()

while True:
    cl, addr = s.accept()
    request = str(cl.recv(1024))
    print(request)
    print(request.find('Referer: '))
    print('client connected from', addr)
    print('temperature', d.temperature())
    print('humidity', d.humidity())

    response = 'temperature: ' + str(d.temperature()) + ', humidity: ' + str(d.humidity())
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
