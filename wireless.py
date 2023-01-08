import network
import socket
import machine
import dht

import myssd1306

i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

import json
import time

ssid = 'overbye_main'
password = '1234567890'

h1 = "<h1>"
h1c = "</h1>"
br = "<br />"


def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        oled.fill(0)
        oled.text('Connecting...', 0, 0, 1)
        oled.show()
        print('Connecting to Wi-Fi...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass

    oled.fill(0)
    oled.text('Connected', 0, 0, 1)
    oled.text('IP:', 0, 10, 1)
    oled.text(sta_if.ifconfig()[0], 0, 20, 1)
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

    response = 'Temperature: ' + str(d.temperature()) + br + 'Humidity: ' + str(d.humidity())
    cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    cl.send(h1 + response + h1c)
    cl.close()
