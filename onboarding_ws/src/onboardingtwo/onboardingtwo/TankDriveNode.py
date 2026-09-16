import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from custom_interfaces.msg import ControlMessage
from custom_interfaces.srv import AxisState


class TankDriveNode(Node):

    def __init__(self):
        super().__init__('tank_drive_node')

        self.declare_parameter('max_vel', 5.0)

    
        self.control_pub = self.create_publisher(
            ControlMessage, '/odrive_axis0/control_message', 10
        )

        
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )

    
        self.axis_state_client = self.create_client(
            AxisState, '/odrive_axis0/request_axis_state'
        )

        self.get_logger().info('TankDriveNode has been initialized.')

    def send_axis_state_request(self, state):
        if not self.axis_state_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warn('Axis state service not available.')
            return

        request = AxisState.Request()
        request.axis_requested_state = state

        future = self.axis_state_client.call_async(request)
        future.add_done_callback(self.axis_state_response_callback)

    def axis_state_response_callback(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'Axis state request succeeded: {response}')
        except Exception as e:
            self.get_logger().error(f'Axis state service call failed: {e}')

    def cmd_vel_callback(self, msg):
        
        max_vel = self.get_parameter('max_vel').value

       
        output_speed = msg.linear.x * max_vel

        # Construct and publish the ControlMessage
        control_msg = ControlMessage()
        control_msg.control_mode = 1
        control_msg.input_mode = 2
        control_msg.input_vel = output_speed
        self.control_pub.publish(control_msg)

        # Check angular.z for IDLE state request (1 -> IDLE, state 1)
        if msg.angular.z == 1:
            self.get_logger().info('Setting axis state to IDLE (1)')
            self.send_axis_state_request(1)

        # Check angular.x for CLOSED_LOOP_CONTROL state request (1 -> CLOSED_LOOP_CONTROL, state 8)
        if msg.angular.x == 1:
            self.get_logger().info('Setting axis state to CLOSED_LOOP_CONTROL (8)')
            self.send_axis_state_request(8)


def main(args=None):
    rclpy.init(args=args)
    node = TankDriveNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()