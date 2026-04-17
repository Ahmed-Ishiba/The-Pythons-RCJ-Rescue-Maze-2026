import VL53L1X
import RPi.GPIO as GPIO
import time

XSHUT1 = 6
XSHUT2 = 19

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(XSHUT1, GPIO.OUT)
GPIO.setup(XSHUT2, GPIO.OUT)
GPIO.output(XSHUT1, False)
GPIO.output(XSHUT2, False)

GPIO.output(XSHUT1, True)

tof1 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof1.open()
tof1.change_address(new_address = 0x28)

tof1.open()

GPIO.output(XSHUT2, True)

tof2 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof2.open()
tof2.change_address(new_address = 0x2a)

tof2.open()

while True:
    tof1.start_ranging(1)
    tof2.start_ranging(1)
    print("distance 1: ", tof1.get_distance())
    print("distance 2: ", tof2.get_distance())