import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String
from custom_msg.msg import ToFData

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

    def tof_cb(self, msg:ToFData):
        self.front_dist = msg.front
        self.right_dist = msg.right
        self.left_dist = msg.left
        self.compute()
        
    def compute(self):
        if None in (self.front_dist, self.right_dist, self.left_dist):
            current_msg.data = "N/A"
        right_clear = self.right_dist > WALL_DIST_RIGHT  #no right wall 
        front_clear = self.front_dist > WALL_DIST_FRONT  #no front wall
        left_clear  = self.left_dist  > WALL_DIST_LEFT  #no right wall
        current_msg = String()

        if right_clear and self.last_msg != 'R':
            current_msg.data = 'R'
        elif front_clear:
            current_msg.data = 'F'
        elif left_clear:
            current_msg.data = 'L'
        else:
            current_msg.data = 'L'

        if current_msg.data != self.last_msg:
            self.pub_cmd.publish(current_msg)
            self.get_logger().info(current_msg.data)
            self.last_msg = current_msg.data


def main(args=None):
    rclpy.init(args=args)
    node = right_hand()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
            