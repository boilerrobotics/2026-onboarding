import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from odrive_can.srv import AxisState
from odrive_can.msg import ControlMessage, ControllerStatus, ODriveStatus
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
        super().__init__("TankDriveNode")

        #qos
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




        #subscription to cmd vel coming from joy node
        self._subscription = self.create_subscription(
            Twist,
            "cmd_vel",
            self.drive_callback,
            self.qos_publish


        )

        self.declare_parameter("max_speed", 5.0)
        #max speed parameter
        self.wheelctrl = self.create_publisher(ControlMessage, "/odrive_axis0/control_message", self.ctrl_msg_qos)
        #control message custom class publisher
        self.wheelsrv = self.create_client(AxisState, "/odrive_axis0/request_axis_state")
        #wheel servo custom class client

        


    def req_state(self, state):
        req = AxisState.Request()
        req.axis_requested_state = state
        future = self.wheelsrv.call_async(req)
        future.add_done_callback(self.wheel_srv_callback)


    def wheel_srv_callback(self, future):
        if future.result().procedure_result ==0:
            self.get_logger().info("Result received")
        else:
            self.get_logger().info("Failed")

        

    def drive_callback(self, msg: Twist):
        speed = msg.linear.x

        out = ControlMessage()
        out.input_vel = float(speed * self.get_parameter("max_speed").value)
        out.control_mode = 2
        out.input_mode = 1

        if (msg.angular.z==1):
            self.req_state(1)
            # idle

        if (msg.angular.x==1):
            self.req_state(8)
            #closed loop

        self.wheelctrl.publish(out)


def main(args=None):
    rclpy.init(args=args)
    TankNode = TankDriveNode()
    rclpy.spin(TankNode)
    TankNode.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()








