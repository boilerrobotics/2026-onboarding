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

One thing you do need to know, however, is how to source your underlays and overlays. Sourcing gives you access to the ROS2 command line instructions, which are much like the linux command line instructions, except specific to ROS2. Take a look at the reference doc for a few useful ones. 

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
```

#### Examine the code
The first lines of code after the comments import rclpy so its Node class can be used.

```python
import rclpy
from rclpy.node import Node
```
The next statement imports the built-in std_msgs/msg/String message type that the node uses to structure the data that it passes on the topic, as well as the service to set the name that it publishes. The reason it's called UpdateFilename is because this service is usually used to update filenames, we're just using it for a different purpose. 

```python
from std_msgs.msg import String
from pcl_msgs.srv import UpdateFilename
```
These lines represent the node’s dependencies. Recall that dependencies have to be added to package.xml, which you’ll do in the next section.

Next, the Talker class is created, which inherits from (or is a subclass of) Node.

``` python
class Talker(Node):
```

Following is the definition of the class’s constructor. super().__init__ calls the Node class’s constructor and gives it your node name, in this case talker.

create_publisher declares that the node publishes messages of type std_msgs/msg/String (imported from the std_msgs.msg module), over a topic named topic, and that the “queue size” is 10. Queue size is a required Quality of Service (QoS) setting that limits the amount of queued messages if a subscriber is not receiving them fast enough.

create_client creates the client that we use to update the name the listener prints. We request the listener to change the name it prints to this talker's "Name" parameter every .5s, as discussed next.

Next, create_timer is used to create 2 callback that executes every 0.5 seconds. The first callback publishes a number every .5 seconds, and the second callback constantly calls a service to change the listener's name to the talker's "Name" parameter. self.i is a counter used in the publisher.

Lastly, "declare_parameter" declares the "Name" parameter with a default value of "Ben", meaning that this is the first value that the talker will request that the listener changes its name to. 

```python
 def __init__(self):
        super().__init__('talker')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.client = self.create_client(UpdateFilename, 'name')

        self.timer1 = self.create_timer(timer_period, self.publisher_callback)
        self.timer2 = self.create_timer(timer_period, self.change_name_request)
        self.i = 0
        self.declare_parameter("Name", "Ben")
```

publisher_callback creates a message with the counter value appended, publishes it, and prints it to the console with get_logger()’s info() function.
To see how the "String()" message is defined, in terminal run
```bash
ros2 interface show std_msgs/msg/String
```
You should see a "data" field, which is what we're modiying here. 

```python
def publisher_callback(self):
    msg = String() # defines the message as a string message 
    msg.data = str(self.i) # populates message's fields
    self.publisher_.publish(msg) # publishes message
    self.get_logger().info('Publishing: "%s"' % msg.data) # prints to terminal that its publishing
    self.i += 1
```

change_name_request requests the listener to change its name every 0.5 seconds (as according to timer2). 
To see the "UpdateFilename" service definition, run 
```bash
ros2 interface show pcl_msgs/srv/UpdateFilename
```
You should see a field, a line with dashes, and another field. The field on top is the "Request" -- this is the data that's sent to the server by the client, and the field below the dashed line is the "Response", which is the part the server sends back to the client after completing the request to acknowledge it. 

At the end of the function we add a callback so once the server finishes the request, we can check for success.

```python
def change_name_request(self):
    self.name = self.get_parameter("Name").value # gets the Name parameter's latest value (in case it was updated)
    req = UpdateFilename.Request() # defines "req" as the "Request" part of the UpdateFilename message, which is the part that contains data to send to the server -- the part above the dashed line
    req.filename = self.name # As you saw earlier, the "Request" portion has 1 field named filename
    future = self.client.call_async(req) # We make the request with "call_async"
    future.add_done_callback(self.check_success) # We add a callback so once the server finishes the request, we can check for success
```

This is the callback passed to the future. It's called as soon as the server completes the request, and processes the "result" that it returns (which has one field called "success" for the UpdateFilename type), and here it prints if the name change failed. 

```python
def check_success(self,future):
    if not future.result().success:
        self.get_logger().info("Name Change Failed") 
```

Lastly, the main function is defined.

```python
def main(args=None):
    rclpy.init(args=args) # init ros2

    talker = Talker() # create and initialize the node

    rclpy.spin(talker) # spin the node

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    talker.destroy_node() # destroy the node
    rclpy.shutdown()
```

First the rclpy library is initialized, then the node is created, and then it “spins” (starts) the node (using spin()) so its callbacks are called.

### 1.6 Add Dependencies 
In the program, we use "rclpy", "std_msgs", and "pcl_msgs". These are standard ROS libraries included in the Docker container - rclpy is the python API, and std_msgs is a package which contains standard message types for topics like strings, integers, and so on. While we imported them in the Python, we need to tell the build tool to include them in the build. 

Navigate to the onboarding_ws/src/<your_package_name> directory, where the setup.py, setup.cfg, and package.xml files have been created for you (by ROS2 pkg create).

You'll see fields like "maintainer", "maintainer email", "description", and so on--it's generally good pratice to fill these in, and required if you plan to publish your work for others to use, but not strictly necessary. If you change them here, you'll also have to change them in setup.py. 

To add your dependencies, add these 3 lines to the file:

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
<exec_depend>pcl_msgs</exec_depend>
```

This declares the package needs rclpy, std_msgs, and pcl_msgs when its code is executed.


### 1.7 Add Entry Point

Whenever you create a new node in a package, you need to define that node as one of the package's "entry points", so that the build system recognizes your code as a node and builds it correctly, so you can run it later.

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
    main()
```

The subscriber node’s code is nearly identical to the publisher’s. The constructor creates a subscriber with the same arguments as the publisher using create_subscription and create_client. Recall that the topic name and message type and QoS used by the publisher and subscriber must match to allow them to communicate.

```python
self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
self.server = self.create_service(UpdateFilename, 'name', self.update_name_callback)
self.name = "Ben"
```

The subscriber’s constructor and callback don’t include any timer definition, because it doesn’t need one. Its callback gets called as soon as it receives a message.
Similary for the client, its callback gets called as soon as it receives a request. 

The callback definition simply prints a "Hello" message to the console, along with the latest name the publisher sent to it via service, and the exact "i" that the callback was called for. Recall that the publisher defines 
```python
msg.data = str(self.i)
```
```python
def listener_callback(self, msg):
    self.get_logger().info(f'Hello {self.name}! I heard: {msg.data}')
    # self.name is the name the publisher sent it via service request, and msg.data is the message that it was called for
```

There is one extra piece here not present in the talker. This is the callback that services the talker's request to change the name. Recall that the "UpdateFilename" service type has a "Response" section with one field named "success" - here this callback sets it to True to tell the talker that it successfully changed its name, it changes its name, and returns the response. 

```python
def update_name_callback(self, request, response):
        response.success = True
        self.name = request.filename
        return response
```

The main definition is almost exactly the same, replacing the creation and spinning of the publisher with the subscriber.

```python
def main(args=None):
    rclpy.init(args=args)

    listener = Listener()

    rclpy.spin(listener)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    listener.destroy_node()
    rclpy.shutdown()
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
[INFO] [1788830168.001106192] [talker]: Publishing: "0"
[INFO] [1788830168.459681821] [talker]: Publishing: "1"
[INFO] [1788830168.886830144] [talker]: Publishing: "2"
[INFO] [1788830169.454912161] [talker]: Publishing: "3"
[INFO] [1788830169.931976309] [talker]: Publishing: "4"
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
ros2 topic info <topic_name> # replace with the name of the topic
ros2 topic echo <topic_name>
```


You should see information about the topic, and the messages being printed to the topic -- this is very useful for debugging. You can try the same with "service info" and the service name. 

Lastly, change the name the listener is printing - run
```bash
ros2 param set /talker Name <Some Name>
```
If you switch to the listener terminal, you should see it changed the name to whatever name you chose - the talker saw the parameter value change and requested the listener to change its name, which the listener did. 

You can also try out other commands found in the master reference. 

Once you're done, you can stop the nodes by pressing Ctrl-C in their respective terminals. 

### 1.10 Conclusion
That's it for part 1! You understand the  basics of ROS2 structure and style, which will let you build more advanced projects. Next, we'll move onto the main onboarding project.

## Part 2

You will be implementing the TankDriveNode shown in the diagram, whose purpose is to take joystick inputs and convert them to wheel velocities. The specifications are as follows:

### Required Interfaces:
- cmd_vel subscriber
    - This will read the joystick inputs and process them, changing the information from the Twist 
    type to the ControlMessage type accepted by the ODriveNode. To see the contents of the "Twist" type, look for the "ros2 interface" command in the ROS2 reference doc and use it.
- /odrive_axis0/control_message publisher
    - This will take the processed input from the cmd_vel subscriber's callback and publish it to the /odrive_axis0/control_message topic, so that the ODriveNode can pick see it and drive the motor accordingly. 
- /odrive_axis0/request_axis_state client
    - This will request the ODriveNode to change the motor's state to "CLOSED_LOOP_CONTROL", which is the state where the motor will accept movement/velocity commands. In addition, it will also request motor state to be changed to IDLE, in case you want to turn off the motor. 

### Recommendations:
First, create a new package in the same workspace you created earlier, using the same command. Then, copy the "custom_interfaces" package from the reference workspace and paste it into your workspace. This will allow you to have access to the custom types (ControlMessage and AxisState) that the ODriveNode requires. 

Then, look at the definitions of each of the message/service types. As stated earlier, use the "ros2 interface" command to look at the Twist message type, as it's a default ROS2 type. The other two types are defined in the "custom_interfaces" package you copied, and in addition, take a look at this: 

https://github.com/odriverobotics/ros_odrive/tree/main/odrive_node

This is the documentation for the ODrive node, and what it publishes and subscribes to. If you ever use a pre-written ROS2 node, look for documentation like this.
You'll see that the custom types use numbers to signify states like "CLOSED_LOOP_CONTROL" and "IDLE", as well as input modes for ControlMessage. The way this works is that each number is associated with a state, and you need to use the correct numbers - to make it simpler, I'll provide you with the necessary numbers here:

control_mode: always set this to 1
input_mode: always set this to 2

In the request_axis_state service,

axis_requested_state: 8 for closed_loop_control, 1 for idle

The input /cmd_vel topic you're getting will be formatted like this:
msg.linear.x will have a decimal value between 0-1. Your job is to scale this to the max_speed parameter, so that the output speed is somewhere between 0 to max_speed and proportional to this value.
msg.angular.z will be either 0 or 1. If it's 1, make a request to ODriveNode to set axis state to IDLE. 
msg.angular.x will be either 0 or 1. If it's 1, make a request to ODriveNode to set axis state to CLOSED_LOOP_CONTROL. 

Hint: Do all the processing and publish the ControlMessage and send the AxisState request in the /cmd_vel subscriber's callback, so you don't need a separate timer for publishing. 