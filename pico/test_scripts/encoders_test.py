from machine import Pin, PWM
from encoder import Encoder
import time

#################################
#right motors

motor1_dir = Pin(8,Pin.OUT)
motor1_pwm = PWM(9)

motor1_pwm.freq(20000)  # 20 kHz PWM
enc1 = Encoder(0, 1)
enc2 = Encoder(2, 3)

enc3 = Encoder(4, 5)
enc4 = Encoder(6, 7)

count = 0

while True:
    motor1_dir.value(1)
    motor1_pwm.duty_u16(65535)
    time.sleep (1)
    motor1_dir.value(1)
    motor1_pwm.duty_u16(0)
    time.sleep(1)
    # print("right distance: ",enc1.value())
    # #print("right distance: ",enc3.value())

    print("left distance: ",enc2.value())