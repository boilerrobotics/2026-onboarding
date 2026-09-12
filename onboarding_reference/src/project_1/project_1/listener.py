<<<<<<< HEAD:src/project_1/project_1/listener.py
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
=======
import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from pcl_msgs.srv import UpdateFilename


class Listener(Node):

    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.server = self.create_service(UpdateFilename, 'name', self.update_name_callback)
        self.name = "Ben"

    def listener_callback(self, msg):
        self.get_logger().info(f'Hello {self.name}! I heard: {msg.data}')

    def update_name_callback(self, request, response):
        response.success = True
        self.name = request.filename
        return response


def main(args=None):
    rclpy.init(args=args)

    listener = Listener()

    rclpy.spin(listener)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    listener.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
>>>>>>> 91e708cfe925bd3ccfd65af0b7c14e2008aa630c:onboarding_reference/src/project_1/project_1/listener.py
    main()