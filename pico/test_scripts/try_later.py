from bno08x import *
from i2c import BNO08X_I2C
from machine import I2C, Pin, PWM
from encoder import Encoder
import time

#################################
#right motors

motor1_dir = Pin(8,Pin.OUT)
motor1_pwm = PWM(9)

motor1_pwm.freq(20000)  # 20 kHz PWM

motorL_dir = Pin(10,Pin.OUT)
motorL_pwm = PWM(11)
motorL_pwm.freq(20000)

enc1 = Encoder(0, 1)
enc2 = Encoder(2, 3)

enc3 = Encoder(4, 5)
enc4 = Encoder(6, 7)

count = 0

int_pin = Pin(15, Pin.IN)  # BNO sensor (INT)
reset_pin = Pin(14, Pin.OUT)  # BNO sensor (RST)

address = 0x4a
i2c0 = I2C(0, scl=Pin(17), sda=Pin(16), freq=400_000)
print(f"I2C {hex(address)} found" if address in i2c0.scan() else f"ERROR: I2C not configured")

bno = BNO08X_I2C(i2c0, address=address, reset_pin=reset_pin, int_pin=int_pin)
print("all I2C devices found:", [hex(d) for d in i2c0.scan()])

print("Start")
print("====================================\n")

bno.acceleration.enable(100)
bno.gyro.enable(20)
bno.quaternion.enable(20)
bno.print_report_period()

bno.update_sensors()
yaw, pitch, roll, acc, ts_ms = bno.quaternion.euler_full
start_yaw = yaw

while True:
    bno.update_sensors()
    yaw, pitch, roll, acc, ts_ms = bno.quaternion.euler_full

    # compute angle difference (handles wrap-around)
    diff = (yaw - start_yaw + 360) % 360

    print("yaw:", yaw, " diff:", diff)

    if diff < 90:
        # keep moving
        motor1_dir(1)
        motorL_dir(1)
        motor1_pwm.duty_u16(16383)
        motorL_pwm.duty_u16(16383)

    else:
        # stop motors
        motor1_pwm.duty_u16(0)
        motorL_pwm.duty_u16(0)
        print("Reached 90 degrees")
        break
    #if bno.quaternion.updated:
        # yaw, pitch, roll, acc, ts_ms = bno.quaternion.euler_full
        # print(f"Euler Angle: Yaw: {yaw:+.3f}°   Pitch: {pitch:+.3f}°  Roll {roll:+.3f}° degrees")
        # #print(f"Euler Angle: accuracy={acc}, {ts_ms=:.1f}")        # Notice Gravity acceleration downwards (~9.8 m/s²)

