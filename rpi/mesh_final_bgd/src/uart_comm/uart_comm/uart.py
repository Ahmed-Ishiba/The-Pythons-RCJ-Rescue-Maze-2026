import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial
import time
from custom_msg.srv import GetCmd
from custom_msg.msg import ToFData
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
import threading

UART_PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600
WALL_DIST_FRONT = 140  # mm — tune this


class UARTNode(Node):

    def __init__(self):
        super().__init__('uart_reader')

        self.publisher_raw = self.create_publisher(String, 'uart/raw', 10)

        # Reentrant group for ToF sub and service client
        self.cb_group = ReentrantCallbackGroup()

        # Exclusive group for UART timer — only one read at a time
        self.uart_cb_group = MutuallyExclusiveCallbackGroup()

        # Client uses reentrant group
        self.client = self.create_client(GetCmd, '/request_motion', callback_group=self.cb_group)
        while not self.client.wait_for_service(timeout_sec=3.0):
            self.get_logger().info("Waiting for /request_motion service...")

        # ToF subscriber uses reentrant group
        self.tof_sub = self.create_subscription(
            ToFData, '/tofs_readings', self.tof_cb, 100,
            callback_group=self.cb_group)

        # Timer uses exclusive group — never runs concurrently with itself
        self.timer = self.create_timer(0.01, self.read_uart, callback_group=self.uart_cb_group)

        self.serial_lock = threading.Lock()
        self.front_dist = None
        self.driving_forward = False
        self.stop_pending = False
        self.request_in_flight = False
        self.stop_confirmed = True

        try:
            self.ser = serial.Serial(UART_PORT, baudrate=BAUD_RATE, timeout=1)
            self.ser.reset_input_buffer()
            time.sleep(1)
            self.get_logger().info(f"Serial port {UART_PORT} opened at {BAUD_RATE} baud")
        except serial.SerialException as e:
            self.get_logger().error(f"Error opening serial port: {e}")
            raise e

    def tof_cb(self, msg: ToFData):
        self.front_dist = msg.front

        if self.driving_forward and 0 < self.front_dist < WALL_DIST_FRONT:
            self.driving_forward = False
            self.stop_pending = True

        if self.stop_pending:
            self.send_uart('STOP')

    def read_uart(self):
        try:
            received_data = self.ser.readline()
            received_message = received_data.decode('utf-8').strip()

            if received_message:
                self.get_logger().info(f"Received: {received_message}")

                if received_message == "REQ" and not self.request_in_flight:
                    self.stop_confirmed = True
                    self.stop_pending = False
                    self.request_in_flight = True
                    req = GetCmd.Request()
                    future = self.client.call_async(req)
                    future.add_done_callback(self.handle_response)

                msg = String()
                msg.data = received_message
                self.publisher_raw.publish(msg)

        except Exception as e:
            self.get_logger().error(f"UART read error: {e}")
    
    def handle_response(self, future):
        try:
            response = future.result()
            cmd = response.cmd
            self.get_logger().info(f"Service responded: {cmd}")

            self.driving_forward = (cmd == 'F')
            self.send_uart(cmd)
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")
        finally:
            self.request_in_flight = False

    def send_uart(self, cmd: str):
        try:
            with self.serial_lock:
                self.ser.write((cmd + '\n').encode('utf-8'))
            self.get_logger().info(f"Sent: {cmd}")
        except Exception as e:
            self.get_logger().error(f"UART write error: {e}")

    def destroy_node(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
            self.get_logger().info("Serial port closed")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = UARTNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()