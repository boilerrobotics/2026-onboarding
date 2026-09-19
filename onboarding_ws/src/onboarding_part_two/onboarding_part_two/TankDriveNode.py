import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from custom_interfaces.msg import ControlMessage
from custom_interfaces.srv import AxisState

class Tankdrivenode(Node):

    def __init__(self):
        super().__init__('tank_drive_node')
        self.declare_parameter('max_vel', 5.0)
        self.subscription = self.create_subscription(Twist, 'cmd_vel', self.drive_callback, 10)
        self.publisher = self.create_publisher(ControlMessage, "/odrive0/control_message", 10)
        self.client = self.create_client(AxisState, "/odrive0/request_axis_state")
    
    def drive_callback(self, msg: Twist):
        speed = float(msg.linear.x * self.get_parameter("max_vel").value)
        out = ControlMessage()
        out.control_mode = 1
        out.input_mode = 2
        out.input_vel = speed
        self.publisher.publish(out)

        if msg.angular.z == 1:
            self.request(1)
        elif msg.angular.x == 1:
            self.request(8)

    def request(self, state):
        req = AxisState.Request()
        req.axis_requested_state = state
        self.client.call_async(req)

def main(args=None):
    rclpy.init(args=args)
    tankdrivenode = Tankdrivenode()
    rclpy.spin(tankdrivenode)

    tankdrivenode.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()