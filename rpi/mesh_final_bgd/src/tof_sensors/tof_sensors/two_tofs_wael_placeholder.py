#! /usr/bin/env python3
import rclpy
from rclpy.node import Node
import VL53L1X
from gpiozero import OutputDevice
from custom_msg.msg import ToFData

class tofsNode(Node):
    def __init__(self):
        super().__init__("two_tofs")

        self.xshut1 = OutputDevice(6,  initial_value=False)
        self.xshut2 = OutputDevice(19, initial_value=False)
        self.xshut3 = OutputDevice(13, initial_value=False)

        self.xshut1.on()
        self.tof1 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.tof1.open()
        self.tof1.change_address(new_address=0x28)
        self.tof1.open()

        self.xshut2.on()
        self.tof2 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.tof2.open()
        self.tof2.change_address(new_address=0x2a)
        self.tof2.open()

        self.xshut3.on()
        self.tof3 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.tof3.open()
        self.tof3.change_address(new_address=0x27)
        self.tof3.open()

        self.tof1.set_timing(66000, 70)
        self.tof1.start_ranging(0)
        self.tof2.set_timing(66000, 70)
        self.tof2.start_ranging(0)
        self.tof3.set_timing(66000, 70)
        self.tof3.start_ranging(0)

        self.pub = self.create_publisher(
            ToFData,
            "/tofs_readings",
            10
        )
        self.msg = ToFData()

        self.timer = self.create_timer(0.07, self.readToFs)

    def readToFs(self):  # <-- correctly indented inside class
        d1 = self.tof1.get_distance()
        d2 = self.tof2.get_distance()
        d3 = self.tof3.get_distance()
        self.get_logger().info(f"Right: {d1}, Front: {d2}, Left: {d3}")
        self.msg.right = float(d1)
        self.msg.front = float(d2)
        self.msg.left = float(d3)
        self.pub.publish(self.msg)

def main(args=None):
    rclpy.init(args=args)
    myNode = tofsNode()
    try:
        rclpy.spin(myNode)
    except:
        rclpy.spin(myNode)
    rclpy.shutdown()

if __name__ == "__main__":
    main()