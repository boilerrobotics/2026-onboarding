import rclpy
from custom_interfaces.srv import AxisState
from custom_interfaces.msg import ControlMessage
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
    LivelinessPolicy,
    Duration,
)

class tanker(Node):
    def __init__(self):
        super().__init__('tanker')
        self.qos_publish = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            depth=1,
            durability=DurabilityPolicy.VOLATILE,
            liveliness=LivelinessPolicy.AUTOMATIC,
            lifespan=Duration(seconds=0.1, nanoseconds=0),
        )
        self.ctrl_msg_qos = QoSProfile(history=HistoryPolicy.KEEP_ALL)

        self.qos_sub = QoSProfile(
            history=HistoryPolicy.KEEP_ALL
        )
        self._subscription = self.create_subscription(
                    Twist,
                    "cmd_vel",
                    self.wheel_callback,
                    self.qos_publish,
                )
        self.wheel_ctrl = self.create_publisher(ControlMessage, "/odrive_axis0/control_message", self.ctrl_msg_qos)
        self.wheel_srv = self.create_client(AxisState, "/odrive_axis0/request_axis_state")
        self.i = 0
        self.declare_parameter("max_vel", 5.0)



    def request_state(self, num):
        req = AxisState.Request()
        req.axis_requested_state = num
        future = self.wheel_srv.call_async(req)
        future.add_done_callback(self.check_success)

    def wheel_callback(self, msg: Twist):
        motor = ControlMessage()
        motor.control_mode = 2
        motor.input_mode = 1
        motor.input_vel =  msg.linear.x * self.get_parameter("max_vel").value
        if msg.angular.z == 1:
            self.request_state(1)
        elif msg.angular.x == 1:
            self.request_state(8)
        self.wheel_ctrl.publish(motor)



    def check_success(self,future):
        if not (future.result().procedure_result == 0 or future.result().procedure_result == 1):
            self.get_logger().info("State Change Failed")        


def main(args=None):
    rclpy.init(args=args)

    Tanker = tanker()

    rclpy.spin(Tanker)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    Tanker.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()