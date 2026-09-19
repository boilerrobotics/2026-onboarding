import rclpy
from odrive_can.srv import AxisState
from odrive_can.msg import ControlMessage, ControllerStatus, ODriveStatus
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
        self.ctrl_msg_qos = QoSProfile(history=HistoryPolicy.KEEP_ALL)

        self.qos_sub = QoSProfile(
            history=HistoryPolicy.KEEP_ALL
        )
        self._subscription = self.create_subscription(
            Twist,
            "cmd_vel",
            self.drive_callback,
            self.qos_publish,
        )
        self.declare_parameter("max_speed", 5.0)
        self.wheel_ctrl = self.create_publisher(ControlMessage, "/odrive_axis0/control_message", self.ctrl_msg_qos)
        self.wheel_srv = self.create_client(AxisState, "/odrive_axis0/request_axis_state")
        self.has_errors = False


    def request_state(self, state):
        req = AxisState.Request()
        req.axis_requested_state = state
        future = self.wheel_srv.call_async(req)
        future.add_done_callback(self.check_srv_result)
        self.get_logger().info('Request sent. Yielding thread back to executor...')

    def check_srv_result(self, future):
        if(future.result().procedure_result == 0):
            self.get_logger().info(f'Result received successfully')
        else:
            print("CLOSED_LOOP_CTRL set failed")
            self.get_logger().info(f'Result failure: {future.result().procedure_result}')


    def drive_callback(self, msg: Twist):
        """
        Callback function that receives Twist messages.
        Convert Twist message to wheel speed.
        """
        speed = msg.linear.x

        out = ControlMessage()
        out.input_mode = 0x1
        out.control_mode = 0x2
        out.input_vel = float(speed * self.get_parameter("max_speed").value)

        if(msg.angular.z == 1):
            self.request_state(1)
        elif(msg.angular.x == 1):
            self.request_state(8)

        self.wheel_ctrl.publish(out)


        

def main(args=None):
    rclpy.init(args=args)

    drive_subscriber = TankDriveNode()

    rclpy.spin(drive_subscriber)

    drive_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()