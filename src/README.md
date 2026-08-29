# BRC Onboarding

## Part 1

Summary: 
    We will create a publisher node which will publish messages to a topic, and a subscriber node that will read those messages and print them out. 

Steps:
1. Create a workspace
2. Creating a package
3. Writing the code
4. Setting up the nodes
5. Building
6. Running

---
### 1.1 Creating a ROS2 Workspace
A workspace is a directory containing ROS 2 packages. Before using ROS 2, it’s necessary to source your ROS 2 installation workspace in the terminal you plan to work in. This makes ROS 2’s packages available for you to use in that terminal.

### 1.2 Source your underlay
An "underlay" is a ROS2 workspace that acts as the base of your project. You can build "overlays" on top of your underlay, which allow you to test different versions of nodes, packages, configurations, etc. without disturbing each other. Not a huge deal right now, so don't worry if you don't understand it fully.

One thing you do need to know, however, is how to source your underlays and overlays. Sourcing gives you access to the ROS2 command line instructions, which are much like the linux command line instructions, except specific to ROS2. Take a look at the master README for a few useful ones. 

To source your underlay, which for this specific project will be the base ROS2 installation, run this command:

```bash
source /opt/ros/humble/setup.bash
```

### 1.3 Create your workspace

Best practice is to create a new directory for every new workspace. The name doesn’t matter, but it is helpful to have it indicate the purpose of the workspace. Let’s choose the directory name onboarding_ws, for Onboarding Workspace:


```bash
mkdir -p ~/onboarding_ws/src
cd ~/onboarding_ws/src
```

Another best practice is to put any packages in your workspace into the src directory. The above code creates a src directory inside the workspace and then navigates into it.


### 1.4 Create a package

#### What is a package?
A package is an organizational unit for your ROS 2 code. If you want to be able to install your code or share it with others, then you’ll need it organized in a package. With packages, you can release your ROS 2 work and allow others to build and use it easily.

Package creation in ROS 2 uses ament as its build system and colcon as its build tool. You can use CMake or Python, but we will be using Python. 

#### Create your package

Make sure you are in the src folder before running the package creation command:
```bash
cd ~/onboarding_ws/src
```

```bash
ros2 pkg create --build-type ament_python --license Apache-2.0 <package_name>
```

Replace <package_name> with whatever you want--good practice is to make it something descriptive.

#### Examine package contents

You should see:

> - **`package.xml`** — file containing meta information about the package
> - **`resource/<package_name>`** — marker file for the package
> - **`setup.cfg`** — required when a package has executables, so `ros2 run` can find them
> - **`setup.py`** — contains instructions for how to install the package
> - **`<package_name>/`** — a directory with the same name as your package, used by ROS 2 tools to find your package; contains `__init__.py`

### 1.5 Write the Publisher
Navigate into onboarding_ws/src/<your package name>/<your package name> - this is where you put your source files. 

Create a file called "talker.py"

Copy this code into it. This is the publisher node that will publish regular messages to a topic. 

```python

import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### Examine the code
The first lines of code after the comments import rclpy so its Node class can be used.

```python
import rclpy
from rclpy.node import Node
```
The next statement imports the built-in std_msgs/msg/String message type that the node uses to structure the data that it passes on the topic.

```python
from std_msgs.msg import String
```
These lines represent the node’s dependencies. Recall that dependencies have to be added to package.xml, which you’ll do in the next section.

Next, the MinimalPublisher class is created, which inherits from (or is a subclass of) Node.

``` python
class MinimalPublisher(Node):
```

Following is the definition of the class’s constructor. super().__init__ calls the Node class’s constructor and gives it your node name, in this case minimal_publisher.

create_publisher declares that the node publishes messages of type std_msgs/msg/String (imported from the std_msgs.msg module), over a topic named topic, and that the “queue size” is 10. Queue size is a required Quality of Service (QoS) setting that limits the amount of queued messages if a subscriber is not receiving them fast enough.

Next, create_timer is used to create a callback that executes every 0.5 seconds. self.i is a counter used in the callback.

```python
def __init__(self):
    super().__init__('minimal_publisher')
    self.publisher_ = self.create_publisher(String, 'topic', 10)
    timer_period = 0.5  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.i = 0
```

timer_callback creates a message with the counter value appended, publishes it, and prints it to the console with get_logger()’s info() function.

```python
def timer_callback(self):
    msg = String()
    msg.data = 'Hello World: %d' % self.i
    self.publisher_.publish(msg)
    self.get_logger().info('Publishing: "%s"' % msg.data)
    self.i += 1
```

Lastly, the main function is defined.

```python
def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()
```

First the rclpy library is initialized, then the node is created, and then it “spins” (starts) the node (using spin()) so its callbacks are called.

### 1.6 Add Dependencies 
In the program, we use "rclpy" and "std_msgs". These are standard ROS libraries included in the Docker container - rclpy is the python API, and std_msgs is a package which contains standard message types for topics like strings, integers, and so on. While we imported them in the Python, we need to tell the build tool to include them in the build. 

Navigate to the onboarding_ws/src/<your_package_name> directory, where the setup.py, setup.cfg, and package.xml files have been created for you (by ROS2 pkg create).

You'll see fields like "maintainer", "maintainer email", "description", and so on--it's generally good pratice to fill these in, and required if you plan to publish your work for others to use, but not strictly necessary. If you change them here, you'll also have to change them in setup.py. 

To add your dependencies, add these two lines to the file:

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

This declares the package needs rclpy and std_msgs when its code is executed.


### 1.7 Add Entry Point

Whenever you create a new node in a package, you need to define that node as one of the package's "entry points", so that the build system recognizes your code as a node and builds it correctly, so you can it later.

Navigate to the onboarding_ws/src/<your_package_name> directory again.

Open the setup.py file. 

To add the entry point, add the following inside the 'console scripts' like so in setup.py:

```python
entry_points={
        'console_scripts': [
                'talker = <your package name>.talker:main',
        ],
},
```

This tells the build tool to create a node named "talker" using the "main" function of the "talker.py" file present in your package.

### 1.7 Write the Subscriber node
Create a file called "listener.py" in the same directory as the talker.

Copy this code into it. This is the subscriber that will listen to the talker's messages and print them out. 

```python
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
    main()
```
The subscriber node’s code is nearly identical to the publisher’s. The constructor creates a subscriber with the same arguments as the publisher using create_subscription. Recall from the topics tutorial that the topic name and message type used by the publisher and subscriber must match to allow them to communicate.

```python
self.subscription = self.create_subscription(
    String,
    'topic',
    self.listener_callback,
    10)
```

The subscriber’s constructor and callback don’t include any timer definition, because it doesn’t need one. Its callback gets called as soon as it receives a message.

The callback definition simply prints an info message to the console, along with the data it received. Recall that the publisher defines 
```python
msg.data = 'Hello World: %d' % self.i
```
```python
def listener_callback(self, msg):
    self.get_logger().info('I heard: "%s"' % msg.data)
```

The main definition is almost exactly the same, replacing the creation and spinning of the publisher with the subscriber.

```python
minimal_subscriber = MinimalSubscriber()

rclpy.spin(minimal_subscriber)
```

Since this node has the same dependencies as the publisher, there’s nothing new to add to package.xml.

### 1.8 Add Entry Point

Reopen setup.py and add the entry point for the subscriber node below the publisher’s entry point. The entry_points field should now look like this:

```python
entry_points={
        'console_scripts': [
                'talker = <your_package_name>.talker:main',
                'listener = <your_package_name>.listener:main',
        ],
},
```

### 1.9 Build and Run
Navigate to your workspace root: onboarding_ws/

Run

```bash
colcon build --packages-select <my_package_name>
```

This tells colcon to build your package in this workspace. 

Useful flags:

| Flag | Effect |
|---|---|
| `--packages-select <name>` | Build only the named package(s) |
| `--packages-up-to <name>` | Build a package and everything it depends on |

After a build, you'll see three new directories:

- `build/` — intermediate build files
- `install/` — the installed packages you'll actually source and run
- `log/` — build logs

Open a new terminal (3 dots on the top of your screen, and "new terminal"), navigate to onboarding_ws, and source the setup files:

```bash
source install/setup.bash
```

Like you sourced your underlay at the start of this, which made all ROS commands available, this sources your overlay--which makes the package you just built available. 

Run your talker:
```bash
ros2 run <my_package_name> talker
```

It should start publishing messages like this:
```bash
ros2 run <my_package_name> talker
[info] [minimal_publisher]: publishing: "hello world: 0"
[info] [minimal_publisher]: publishing: "hello world: 1"
[info] [minimal_publisher]: publishing: "hello world: 2"
[info] [minimal_publisher]: publishing: "hello world: 3"
[info] [minimal_publisher]: publishing: "hello world: 4"
```

Open another terminal, source your overlay again, and start the listener. 
```bash
ros2 run <my_package_name> listener
```

Your listener will start listening to the talker and printing messages the talker saves to the topic. 

Next, open a third terminal and run
```bash
ros2 node list
```

You should see your two nodes running. 

Run 
```bash
ros2 topic list
```

You should see the topic the nodes are talking over. 

Run
```bash
ros2 topic info <topic_name>
ros2 topic echo <topic_name>
```

You should see information about the topic, and the messages being printed to the topic -- this is very useful for debugging. 
You can also try out other commands found in the master reference. 

Once you're done, you can stop the nodes by pressing Ctrl-C in their respective terminals. 

### 1.10 Conclusion
That's it for part 1! You understand the very basics of ROS2 structure and style, which will let you build more advanced projects. Next, we'll move onto the main onboarding project, which is making a wheel spin with a joystick. 


## Part 2