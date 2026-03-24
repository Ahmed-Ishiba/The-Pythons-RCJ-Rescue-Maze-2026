from encoder import *
from bno08x import *
from i2c import BNO08X_I2C
from machine import I2C, Pin, PWM

Kp = 1.2

def forward_for(motor_channel_1:Motor, motor_channel_2:Motor, speed:int, target_distance:int, encoder:Encoder):
    initial = encoder.distance_value()
    #print(initial)
    motor_channel_1.forward(speed)
    motor_channel_2.forward(speed)
    while (int(encoder.distance_value()) - initial) < target_distance:
        motor_channel_1.forward(speed)
        motor_channel_2.forward(speed)
        #print(encoder.distance_value())
        utime.sleep(1)
    motor_channel_1.stop()
    motor_channel_2.stop()

def rotate_for(right_motor_channel:Motor, left_motor_channel:Motor, speed:int, angle_of_rotation:int, IMU_object:BNO08X):
    IMU_object.update_sensors()
    initial_yaw = IMU_object.quaternion.euler_full[0]
    target_yaw = angle_of_rotation + initial_yaw

    while True:
        IMU_object.update_sensors()
        current_yaw = IMU_object.quaternion.euler_full[0]
        print(current_yaw)
        error = target_yaw - current_yaw
        if abs(error) <= 1:
            break
        correction = error * Kp

        correction = max(min(correction, speed),-speed)
        left_motor_channel.forward(abs(int(correction))) if correction > 0 else left_motor_channel.reverse(abs(int(correction)))
        right_motor_channel.reverse(abs(int(correction))) if correction > 0 else right_motor_channel.forward(abs(int(correction)))
    right_motor_channel.stop()
    left_motor_channel.stop()

    