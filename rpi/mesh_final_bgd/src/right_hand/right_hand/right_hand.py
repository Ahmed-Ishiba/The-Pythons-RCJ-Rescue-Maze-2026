import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String
from custom_msg.msg import ToFData
from custom_msg.srv import GetCmd

WALL_DIST_FRONT = 100
WALL_DIST_RIGHT = 110
WALL_DIST_LEFT = 110

class right_hand(Node):
    def __init__(self):
        super().__init__('righHand')
        self.front_dist = None
        self.left_dist = None
        self.right_dist = None
        self.readings = self.create_subscription(ToFData, '/tofs_readings',self.tof_cb, 10)
        self.last_msg = 'X'
        self.pub_cmd = self.create_publisher(String, '/uart/send',10)
        self.server = self.create_service(GetCmd, '/request_motion', self.compute)

    def tof_cb(self, msg:ToFData):
        self.front_dist = msg.front
        self.right_dist = msg.right
        self.left_dist = msg.left
        # self.compute()
        
    def compute(self, request, response):
        if None in (self.front_dist, self.right_dist, self.left_dist):
            response.cmd = 'N/A'
            return response

        right_clear = self.right_dist > WALL_DIST_RIGHT
        front_clear = self.front_dist > WALL_DIST_FRONT
        left_clear  = self.left_dist  > WALL_DIST_LEFT

        if right_clear and self.last_msg == 'F':
            cmd = 'R'
        elif front_clear:
            cmd = 'F'
        elif left_clear:
            cmd = 'L'
        else:
            cmd = 'L'

        self.get_logger().info(f'Decided: {cmd} | F:{self.front_dist} R:{self.right_dist} L:{self.left_dist}')
        self.last_msg = cmd
        response.cmd = cmd
        return response

def main(args=None):
    rclpy.init(args=args)
    node = right_hand()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
            