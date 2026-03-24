from machine import I2C, Pin, PWM
from encoder import *
from advanced_motion import *
from bno08x import *
from i2c import BNO08X_I2C
import time

motorL = Motor(8,9,1)
motorR = Motor(10,11,0)

enc1 = Encoder(0,1, 0)
enc2 = Encoder(1,3, 2)

enc3 = Encoder(2,5, 4)
enc4 = Encoder(3,6, 7) #back left

count = 0
enc1.reset()
enc2.reset()
enc3.reset()
enc4.reset()

int_pin = Pin(15, Pin.IN)  # BNO sensor (INT)
reset_pin = Pin(14, Pin.OUT)  # BNO sensor (RST)

address = 0x4a
i2c0 = I2C(0, scl=Pin(17), sda=Pin(16), freq=400_000)
#print(f"I2C {hex(address)} found" if address in i2c0.scan() else f"ERROR: I2C not configured")

bno = BNO08X_I2C(i2c0, address=address, reset_pin=reset_pin, int_pin=int_pin)
# print("all I2C devices found:", [hex(d) for d in i2c0.scan()])

# print("Start")
# print("====================================\n")

bno.acceleration.enable(100)
bno.gyro.enable(20)
bno.quaternion.enable(20)
bno.print_report_period()

while True:
    bno.update_sensors()
    print(bno.quaternion.euler_full[0])
    rotate_for(motorR, motorL, 100, 90, bno)
    #forward_for(motorL, motorR,100, 10, enc2)
    break
    # time.sleep(1)
    motorL.forward(100)
    motorR.forward(100)
    print("encoder 1 distance in cm: ",enc1.value())
    print("encoder 2 distance in cm: ",enc2.value())
    
    
    # print("right distance: ",enc1.value())
    # #print("right distance: ",enc3.value())
motorL.stop()
motorR.stop()