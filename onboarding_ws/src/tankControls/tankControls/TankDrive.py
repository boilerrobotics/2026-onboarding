import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from odrive_can.srv import AxisState
from odrive_can.msg import ControlMessage, ControllerStatus, ODriveStatus
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
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
        super().__init__('tank_drive')
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
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.subscriber_callback,
            self.qos_publish)
        self.publisher_ = self.create_publisher(ControlMessage, '/odrive_axis0/control_message', self.ctrl_msg_qos)
        self.client = self.create_client(AxisState, '/odrive_axis0/request_axis_state')
        self.declare_parameter("max_speed", 5.0)
       
    def subscriber_callback(self, msg):
        control_msg = ControlMessage()
        control_msg.control_mode = 2
        control_msg.input_mode = 1
        if msg.angular.z == 1:
            self.request_axis_state(1)
        if msg.angular.x == 1:
            self.request_axis_state(8)
        control_msg.input_vel = msg.linear.x * self.get_parameter("max_speed").value
        self.publisher_.publish(control_msg)
        #self.get_logger().info(f'Publishing: velocity={control_msg.input_vel}, position={control_msg.input_pos}')


    def request_axis_state(self, num):
        req = AxisState.Request()
        req.axis_requested_state = num
        future = self.client.call_async(req)
        future.add_done_callback(self.check_success)
        
    def check_success(self,future):
        if future.result().procedure_result == 0:
            self.get_logger().info("Failed")




def main(args=None):
    rclpy.init(args=args)
    
    tankDrive = TankDriveNode()
    
    rclpy.spin(tankDrive)
    
        # Destroy the node explicitly
        # (optional - otherwise it will be done automatically
        # when the garbage collector destroys the node object)
    tankDrive.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()