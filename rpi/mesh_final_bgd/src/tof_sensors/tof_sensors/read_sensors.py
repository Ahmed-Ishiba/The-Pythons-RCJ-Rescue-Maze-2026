from gpiozero import Device,DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
import time
Device.pin_factory = LGPIOFactory()

import VL53L1X
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class TOFSensor(Node):
    def __init__(self):
        super().__init__('tof_sensor')
        
        self.xshut_pins = [DigitalOutputDevice(19),DigitalOutputDevice(6)]
        self.xshut_pins[0].off()
        
        self.sensors =[]
        self.addresses =[0x30,0x31]
        
        
        self.xshut_pins[0].on()
        sensor = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        sensor.open()
        sensor.change_address(self.addresses[0])
        # sensor.open()
        sensor.start_ranging(2)
        self.sensors.append(sensor)
        self.get_logger().info(f"{len(self.sensors)} sensors initialized")
        

        # self.xshut_pins[1].on()
        # sensor2 = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        # sensor2.open()
        # sensor2.change_address(self.addresses[1])
        # sensor2.open()
        # sensor2.start_ranging(2)
        # self.sensors.append(sensor2)
        # self.get_logger().info(f"{len(self.sensors)} sensors initialized")

        self.pub_front = self.create_publisher(Int32, 'tof/front',10)
        self.pub_right = self.create_publisher(Int32, 'tof/right',10)
        self.pub_left = self.create_publisher(Int32, 'tof/left',10)
        
        self.timer = self.create_timer(0.01,self.publish_distance)
    def publish_distance(self):
        try:
            distances= [s.get_distance() for s in self.sensors]
        except:
            self.get_logger().info("Error appending distances")    
        msg = Int32()
        
        msg.data = distances[0]
        self.pub_front.publish(msg)
        
        msg.data = distances[1]
        self.pub_left.publish(msg)

        msg.data = 0
        self.pub_right.publish(msg)

        self.get_logger().info(f"Front {distances[0]}  Right{distances[1]}")

def main(args=None):
    rclpy.init(args=args)
    node = TOFSensor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
