import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import time


UART_PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600


class UARTNode(Node):

    def __init__(self):

        super().__init__('uart_reader')

        self.publisher_ = self.create_publisher(String, 'uart/data', 10)

        try:
            self.ser = serial.Serial(
                UART_PORT,
                baudrate=BAUD_RATE,
                timeout=1
            )
            self.ser.reset_input_buffer()

            time.sleep(1)

            self.get_logger().info(
                f"Serial port {UART_PORT} opened at {BAUD_RATE} baud"
            )

        except serial.SerialException as e:

            self.get_logger().error(f"Error opening serial port: {e}")
            raise e

        # timer runs every 0.1 seconds
        self.timer = self.create_timer(0.1, self.read_uart)

    def read_uart(self):
        #self.get_logger().info("checking uart...")
        try:
            received_data = self.ser.readline()

            received_message = received_data.decode('utf-8').strip()

            msg = String()
            msg.data = received_message

            self.publisher_.publish(msg)

            self.get_logger().info(
                f"Received: {msg.data}"
            )

        except Exception as e:

            self.get_logger().error(f"UART read error: {e}")

    def destroy_node(self):

        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            self.get_logger().info("Serial port closed")

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = UARTNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()    