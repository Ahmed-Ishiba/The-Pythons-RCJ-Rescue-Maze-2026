#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import VL53L1X
from gpiozero import OutputDevice
from custom_msg.msg import ToFData
import time
import signal
import sys

class tofsNode(Node):
    def __init__(self):
        super().__init__("two_tofs")
        self.xshut1 = OutputDevice(6,  initial_value=False)
        self.xshut2 = OutputDevice(19, initial_value=False)
        self.xshut3 = OutputDevice(13, initial_value=False)
        self.tof1 = None
        self.tof2 = None
        self.tof3 = None

        self.init_tofs()

        self.pub = self.create_publisher(ToFData, "/tofs_readings", 10)
        self.msg = ToFData()
        self.timer = self.create_timer(0.01, self.readToFs)

    def init_tofs(self, retries=5):
        for attempt in range(retries):
            try:
                self.get_logger().info(f"Initializing ToF sensors (attempt {attempt + 1}/{retries})...")

                # Reset all sensors first by cycling XSHUT pins
                self.xshut1.off()
                self.xshut2.off()
                self.xshut3.off()
                time.sleep(0.1)

                # Bring up sensor 1 and reassign address
                self.xshut1.on()
                time.sleep(0.05)
                self.tof1 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
                self.tof1.open()
                self.tof1.change_address(new_address=0x28)
                self.tof1.open()

                # Bring up sensor 2 and reassign address
                self.xshut2.on()
                time.sleep(0.05)
                self.tof2 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
                self.tof2.open()
                self.tof2.change_address(new_address=0x2a)
                self.tof2.open()

                # Bring up sensor 3 and reassign address
                self.xshut3.on()
                time.sleep(0.05)
                self.tof3 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
                self.tof3.open()
                self.tof3.change_address(new_address=0x27)
                self.tof3.open()

                # Configure and start ranging
                for tof in [self.tof1, self.tof2, self.tof3]:
                    tof.set_timing(20000, 25)
                    tof.start_ranging(0)

                self.get_logger().info("ToF sensors initialized successfully")
                return  # Success — exit the retry loop

            except Exception as e:
                self.get_logger().error(f"ToF init failed (attempt {attempt + 1}): {e}")
                # Stop ranging on any sensors that started before the failure
                for tof in [self.tof1, self.tof2, self.tof3]:
                    try:
                        if tof is not None:
                            tof.stop_ranging()
                    except:
                        pass
                self.tof1 = None
                self.tof2 = None
                self.tof3 = None
                time.sleep(0.5)  # Wait before retrying

        self.get_logger().error("ToF initialization failed after all retries — check wiring")

    def readToFs(self):
        # If sensors aren't initialized, try again before reading
        if None in (self.tof1, self.tof2, self.tof3):
            self.get_logger().warn("Sensors not ready, retrying init...")
            self.init_tofs()
            return  # Skip this read cycle, try next timer tick

        try:
            d1 = self.tof1.get_distance()
            d2 = self.tof2.get_distance()
            d3 = self.tof3.get_distance()

            if 0 in (d1, d2, d3):
                self.get_logger().warn("Invalid ToF reading (0), skipping publish")
                return   # don't publish bad data at all

            self.get_logger().info(f"Right: {d1}, Front: {d2}, Left: {d3}")
            self.msg.right = float(d1)
            self.msg.front = float(d2)
            self.msg.left = float(d3)
            self.pub.publish(self.msg)

        except Exception as e:
            self.get_logger().error(f"ToF read error: {e} — reinitializing...")
            for tof in [self.tof1, self.tof2, self.tof3]:
                try:
                    if tof is not None:
                        tof.stop_ranging()
                except:
                    pass
            self.tof1 = None
            self.tof2 = None
            self.tof3 = None
            # init_tofs will be called on the next timer tick via the None check above
def signal_handler(sig, frame):
    print("\n[INFO] Force stopping node...")
    rclpy.shutdown()
    sys.exit(0)

def main(args=None):
    signal.signal(signal.SIGINT, signal_handler)
    rclpy.init(args=args)
    myNode = tofsNode()
    try:
        rclpy.spin(myNode)
    except KeyboardInterrupt:
        pass
    finally:
        myNode.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()