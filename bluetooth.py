import json
from machine import Pin
from machine import Timer
from machine import PWM
from time import sleep_ms
import helpers
import ubluetooth

from dcmotor import DCMotor

frequency = 15000

m_left_enable = PWM(Pin(14), frequency)
m_left_pin1 = Pin(26, Pin.OUT)
m_left_pin2 = Pin(27, Pin.OUT)

m_right_enable = PWM(Pin(25), frequency)
m_right_pin1 = Pin(33, Pin.OUT)
m_right_pin2 = Pin(32, Pin.OUT)

dc_motor_left = DCMotor(m_left_pin1, m_left_pin2, m_left_enable)
dc_motor_right = DCMotor(m_right_pin1, m_right_pin2, m_right_enable)

dc_motor_left = DCMotor(m_left_pin1, m_left_pin2, m_left_enable, 0, 1023)
dc_motor_right = DCMotor(m_right_pin1, m_right_pin2, m_right_enable, 0, 1023)

# servo1 = PWM(Pin(27), freq=50, duty_ns=1600000)
# servo2 = PWM(Pin(26), freq=50, duty_ns=1600000)

ble_msg = ""


class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)

        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))

    def ble_irq(self, event, data):
        global ble_msg

        if event == 1:  # _IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral
            self.connected()

        elif event == 2:  # _IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()

        elif event == 3:  # _IRQ_GATTS_WRITE:
            # A client has written to this characteristic or descriptor.
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()

    def register(self):
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)

        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART,)
        ((self.tx, self.rx,),) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")
        # adv_data
        # raw: 0x02010209094553503332424C45
        # b'\x02\x01\x02\t\tESP32BLE'
        #
        # 0x02 - General discoverable mode
        # 0x01 - AD Type = 0x01
        # 0x02 - value = 0x02

        # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
        # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics


led = Pin(2, Pin.OUT)
but = Pin(0, Pin.IN)
ble = ESP32_BLE("ESP32BLE")

prev_ble_msg = ''


def buttons_irq(pin):
    led.value(not led.value())
    # ble.send('LED state will be toggled.')
    print('LED state will be toggled.')


but.irq(trigger=Pin.IRQ_FALLING, handler=buttons_irq)


def set_motors_speed(var_l, var_r):
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
    if (bool(ble_msg) and ble_msg != prev_ble_msg):
        json_object = json.loads(ble_msg)
        remote_data = helpers.RemoteData(**json_object)
        print(ble_msg)
        var_l = remote_data.l
        var_r = remote_data.r

        # print('l =', var_l)
        # print('r =', var_r)

        set_motors_speed(var_l, var_r)

        # duty_cycle1 = helpers.scale_value(int(var_l), -100, 100, 600000, 2600000)
        # duty_cycle2 = helpers.scale_value(int(var_r), -100, 100, 600000, 2600000)
        # 0 - 1023 50Hz = 20mc
        # 40 = 1ms / 20ms * 1023 = 51 @ 1000000
        # 117 = 2ms / 20ms * 1023 = 102 @ 2000000
        # servo1.duty_ns(duty_cycle1)
        # servo2.duty_ns(duty_cycle2)
        prev_ble_msg = ble_msg
        ble_msg = ''
    sleep_ms(50)
