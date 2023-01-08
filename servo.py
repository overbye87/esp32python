# servo1 = PWM(Pin(27), freq=50, duty_ns=1600000)
# servo2 = PWM(Pin(26), freq=50, duty_ns=1600000)


# duty_cycle1 = helpers.scale_value(int(var_l), -100, 100, 600000, 2600000)
# duty_cycle2 = helpers.scale_value(int(var_r), -100, 100, 600000, 2600000)
# 0 - 1023 50Hz = 20mc
# 40 = 1ms / 20ms * 1023 = 51 @ 1000000
# 117 = 2ms / 20ms * 1023 = 102 @ 2000000
# servo1.duty_ns(duty_cycle1)
# servo2.duty_ns(duty_cycle2)