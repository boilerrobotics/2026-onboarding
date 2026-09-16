import rclpy
from rclpy.node import Node

from odrive_can.srv import AxisState
from odrive_can.msg import ControlMessage, ControllerStatus, ODriveStatus
from rclpy.qos import qos_profile_sensor_data
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
    LivelinessPolicy,
    Duration,
)


from geometry_msgs.msg import Twist
class TankDriveNode(Node):

    def __init__(self):
        super().__init__('tank_driver_node')

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

        self.publisher_ = self.create_publisher(ControlMessage, '/odrive_axis0/control_message', self.ctrl_msg_qos)
        self.client = self.create_client(AxisState, '/odrive_axis0/request_axis_state')
        self.subscription = self.create_subscription(
                    Twist,
                    'cmd_vel',
                    self.joy_node_callback,
                    self.qos_publish)

            

        self.declare_parameter("max_vel", 5.0)
    
    def joy_node_callback(self, msg):

        if msg.angular.z == 1:
            req = AxisState.Request()
            req.axis_requested_state = 1 # IDLE
            future = self.client.call_async(req)
            future.add_done_callback(self.check_success)
            self.get_logger().info("Changing axis state to IDLE")
            
        if msg.angular.x == 1:
            req = AxisState.Request()
            req.axis_requested_state = 8 # CLOSED_LOOP_CONTROL
            future = self.client.call_async(req)
            future.add_done_callback(self.check_success)
            self.get_logger().info("Changing axis state to CLOSED_LOOP_CONTROL")

        # Publish Message
        draft = ControlMessage()
        draft.control_mode = 2
        draft.input_mode = 1
        draft.input_vel = msg.linear.x * self.get_parameter("max_vel").value

        self.publisher_.publish(draft)

    def check_success(self,future):
        if future.result().procedure_result in [0, 1]:
            self.get_logger().info("Axis State Change Failed") 

def main(args=None):
    rclpy.init(args=args)

    tank_drive = TankDriveNode()
    rclpy.spin(tank_drive)
    tank_drive.destroy_node()

    rclpy.shutdown()

if __name__ == '__main__':
    main()