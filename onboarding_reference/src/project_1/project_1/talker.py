import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from pcl_msgs.srv import UpdateFilename

class Talker(Node):

    def __init__(self):
        super().__init__('talker')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.client = self.create_client(UpdateFilename, 'name')

        self.timer1 = self.create_timer(timer_period, self.publisher_callback)
        self.timer2 = self.create_timer(timer_period, self.change_name_request)
        self.i = 0
        self.declare_parameter("Name", "Ben")

    def publisher_callback(self):
        msg = String()
        msg.data = str(self.i)
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


    def change_name_request(self):
        self.name = self.get_parameter("Name").value
        req = UpdateFilename.Request()
        req.filename = self.name
        future = self.client.call_async(req)
        future.add_done_callback(self.check_success)

    def check_success(self,future):
        if not future.result().success:
            self.get_logger().info("Name Change Failed")        


def main(args=None):
    rclpy.init(args=args)

    talker = Talker()

    rclpy.spin(talker)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    talker.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()