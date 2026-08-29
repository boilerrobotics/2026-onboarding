import asyncio
import rclpy
from custom_interfaces.srv import AxisState
from custom_interfaces.msg import ControlMessage, ControllerStatus, OdriveStatus
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
    LivelinessPolicy,
    Duration,
)

class TankDriveNode(Node):

    def __init__(self):
        super().__init__("ve_subscriber")
        self.qos_publish = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            depth=1,
            durability=DurabilityPolicy.VOLATILE,
            liveliness=LivelinessPolicy.AUTOMATIC,
            lifespan=Duration(seconds=0.1, nanoseconds=0),
        )
        self.qos_sub = QoSProfile(
            history=HistoryPolicy.KEEP_ALL
        )
        self._subscription = self.create_subscription(
            Twist,
            "cmd_vel",
            self.drive_callback,
            self.qos_publish,
        )

        self.top_left_ctrl = self.create_publisher(ControlMessage, "/top_left/control_message", self.qos_publish)
        self.top_left_srv = self.create_client(AxisState, "/top_left/request_axis_state")

        self.top_right_ctrl = self.create_publisher(ControlMessage, "/top_right/control_message", self.qos_publish)
        self.top_right_srv = self.create_client(AxisState, "/top_right/request_axis_state")

        self.bottom_left_ctrl = self.create_publisher(ControlMessage, "/bottom_left/control_message", self.qos_publish)
        self.bottom_left_srv = self.create_client(AxisState, "/bottom_left/request_axis_state")

        self.bottom_right_ctrl = self.create_publisher(ControlMessage, "/bottom_right/control_message", self.qos_publish)
        self.bottom_right_srv = self.create_client(AxisState, "/bottom_right/request_axis_state")

        self.request_closed_loop_ctrl(self.top_left_srv)
        self.request_closed_loop_ctrl(self.top_right_srv)
        self.request_closed_loop_ctrl(self.bottom_left_srv)
        self.request_closed_loop_ctrl(self.bottom_right_srv)


        self.has_errors = False


    def request_closed_loop_ctrl(self, client):
        req = AxisState.Request()
        req.axis_requested_state = 8
        future = client.call_async(req)
        future.add_done_callback(self.check_srv_result)
        self.get_logger().info('Request sent. Yielding thread back to executor...')

    def check_srv_result(self, future):
        if(future.result().procedure_result == 0):
            print("Motor set to CLOSED_LOOP_CTRL")
            self.get_logger().info(f'Result received successfully')
        else:
            print("CLOSED_LOOP_CTRL set failed")
            self.get_logger().info(f'Result failure')

    def update_linear_speed_limit(self):
        self.linear_speed_limit = self.get_parameter("speed_limit").get_parameter_value().double_value


    def drive_callback(self, msg: Twist):
        """
        Callback function that receives Twist messages.
        Convert Twist message to wheel speed.
        """
        left = msg.linear.x
        right = msg.linear.y

        out_left = ControlMessage()
        out_left.input_mode = 0x1
        out_left.control_mode = 0x2
        out_left.input_vel = left

        out_right = ControlMessage()
        out_right.input_mode = 0x1
        out_right.control_mode = 0x2
        out_right.input_vel = right

        self.top_right_ctrl.publish(out_right)
        self.bottom_right_ctrl.publish(out_right)
        self.top_left_ctrl.publish(out_left)
        self.bottom_left_ctrl.publish(out_left)


        

def main(args=None):
    rclpy.init(args=args)

    drive_subscriber = TankDriveNode()

    rclpy.spin(drive_subscriber)

    drive_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()