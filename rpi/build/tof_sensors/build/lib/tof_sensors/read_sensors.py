from gpiozero import Device,DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()


import VL53L1X
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32

class TOFSensor(Node):
    def __init__(self):
        super().__init__('tof_sensor')
        
        self.xshut_pins = [DigitalOutputDevice(6),DigitalOutputDevice(13),DigitalOutputDevice(19)]
        for i in self.xshut_pins:
            i.off()
        
        self.sensors =[]
        self.addresses =[0x30,0x31]
        
        for i ,pin in enumerate(self.xshut_pins):
            pin.on()
            sensor = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
            sensor.open()
            sensor.change_address(self.addresses[i])
            sensor.start_ranging(1)
            self.sensors.append(sensor)
            
        self.pub_front = self.create_publisher(Int32, 'tof/front',10)
        self.pub_right = self.create_publisher(Int32, 'tof/right',10)
        self.pub_left = self.create_publisher(Int32, 'tof/left',10)
        self.timer = self.create_timer(0.1,self.publish_distance)
    def publish_distance(self):
        distances= [s.get_distance() for s in self.sensors]
        msg = Int32()
        
        msg.data = distances[0]
        self.pub_front.publish(msg)
        
        msg.data = distances[1]
        self.pub_left.publish(msg)

        msg.data = distances[2]
        self.pub_right.publish(msg)

        self.get_logger().info(
            f"Front {distances[0]}  Left {distances[1]}  Right {distances[2]}")

def main(args=None):
    rclpy.init(args=None)
    node = TOFSensor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
