import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from odrive_can.msg import ControlMessage
from odrive_can.srv import AxisState
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import SetParametersResult
from rclpy.qos import (
    QoSProfile,
    ReliabilityPolicy,
    HistoryPolicy,
    DurabilityPolicy,
    LivelinessPolicy,
    Duration,
)

#print(AxisState.CLOSED_LOOP_CONTROL) # 8
#print(AxisState(8).name) # CLOSED_LOOP_CONTROL

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
        self.qos_sub = QoSProfile (
            history=HistoryPolicy.KEEP_ALL
        )
        self.control_message_publisher = self.create_publisher(ControlMessage, '/odrive_axis0/control_message', self.ctrl_msg_qos)
        self.declare_parameter("max_vel",5.0)
        self.cmd_vel_subscriber = self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_callback, self.qos_publish)
        self.request_axis_state_client = self.create_client(AxisState, '/odrive_axis0/request_axis_state')
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

    def cmd_vel_callback(self, msg):
        speed = ControlMessage()
        speed.control_mode = 2
        speed.input_mode = 1
        speed.input_vel = msg.linear.x * self.get_parameter("max_vel").value;
        if msg.angular.z == 1:
            self.request_axis_state("IDLE")
        elif msg.angular.x == 1:
            self.request_axis_state("CLOSED_LOOP_CONTROL")

        self.control_message_publisher.publish(speed)

    def request_axis_state(self, state):
        req = AxisState.Request()
        if state == "IDLE":
            req.axis_requested_state = 1
            future = self.request_axis_state_client.call_async(req)
            future.add_done_callback(self.check_success)
        elif state == "CLOSED_LOOP_CONTROL":
            req.axis_requested_state = 8
            future = self.request_axis_state_client.call_async(req)
            future.add_done_callback(self.check_success)

        
        
      
        
        

    def check_success(self,req):
        if req.result().procedure_result == 0 or req.result().procedure_result == 1:
            print("success")
        else:
            print("failure")

def main(args=None):
    rclpy.init(args=args)

    tank_drive_mode = TankDriveNode()

    rclpy.spin(tank_drive_mode)
    rclpy.shutdown()

   
if __name__ == '__main__':
    main()
