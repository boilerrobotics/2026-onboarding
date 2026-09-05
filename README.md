# ROS2 Humble — Stage 1 Dev Container

DevContainer for local development.

## Layout

This uses the standard devcontainer convention: `.devcontainer/` sits at
the root of the repo, alongside your actual ROS2 packages.

```
club-robot/                  ← repo root (this is what gets mounted)
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── src/
│   └── (your ROS2 packages go here)
└── README.md
```

VS Code mounts this *entire folder* into the container and opens the container with that as the working directory. 

## What's inside

- Base image: `osrf/ros:humble-desktop` (includes rviz2, rqt — not just
  `ros-base`)
- `rclpy` (comes with the base ROS2 install)
- `colcon` + `colcon-common-extensions`
- `numpy`, `scipy`, `matplotlib`
- `rosdep`, pre-updated
- VS Code extensions: ROS (`ms-iot.vscode-ros`), Python, Pylance

## Requirements

- [VS Code](https://code.visualstudio.com/) with the **Dev Containers**
  extension (`ms-vscode-remote.remote-containers`)
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- ~10 GB free disk (the desktop image is sizable)

## Getting started

1. Clone the club repo locally.
2. Open the repo folder in VS Code.
3. When prompted, click **"Reopen in Container"** (or run
   `Dev Containers: Reopen in Container` from the command palette).
4. First build takes a few minutes — grab a coffee.
5. Once inside, open a terminal in VS Code (it opens already inside the
   container, at the repo root) and build:
   ```bash
   colcon build
   source install/setup.bash
   ```

Everything under `src/` is a normal file on your host laptop too — the
container is just the environment running it, not a separate copy. Edits
in VS Code, `git` commands, etc. all act on the same files whether you run
them from inside the container's terminal or your host's.

## Creating your first package

```bash
cd src
ros2 pkg create --build-type ament_python my_first_node --dependencies rclpy
cd ..
colcon build --packages-select my_first_node
source install/setup.bash
ros2 run my_first_node <entry_point_name>
```

## GUI apps (rviz2, rqt) — optional, and OS-dependent

Stage 1 work usually doesn't need rviz2 (that's more useful once you have
real or bagged sensor data in Stage 2). If you do want it locally:

**Linux**
```bash
xhost +local:docker
```
Then add to `devcontainer.json`'s `runArgs`:
```json
"runArgs": ["--env=DISPLAY", "--volume=/tmp/.X11-unix:/tmp/.X11-unix:rw"]
```
Rebuild the container. This gives you native X11 forwarding, no extra
software needed.

**macOS**
1. Install [XQuartz](https://www.xquartz.org/), open it, and in
   XQuartz → Settings → Security, enable "Allow connections from network
   clients."
2. Restart XQuartz.
3. In a Mac terminal: `xhost + 127.0.0.1`
4. Add to `devcontainer.json`:
   ```json
   "containerEnv": { "DISPLAY": "host.docker.internal:0" }
   ```
5. Rebuild the container.

**Windows**
1. Install [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or use
   WSLg if you're running Docker Desktop with the WSL2 backend (WSLg
   often just works with no extra server needed).
2. If using VcXsrv: launch it with "Disable access control" checked.
3. Add to `devcontainer.json`:
   ```json
   "containerEnv": { "DISPLAY": "host.docker.internal:0" }
   ```
4. Rebuild the container.

GUI passthrough is genuinely the flakiest part of running ROS2 in Docker
cross-platform — if it's fighting you, it's usually not worth the time for
Stage 1 work. Save the fight for when you actually need to look at a live
camera feed or TF tree (Stage 2).

## Notes

- `ROS_DOMAIN_ID` is pinned to `0` in `containerEnv` for now. Once you set
  up Stage 2 (Jetson + discovery server), you'll add the discovery server
  address here instead — that'll be a separate doc.
- `--network=host` is intentionally commented out. It behaves consistently
  on Linux but not on Docker Desktop for Mac/Windows, and Stage 1 doesn't
  need real network discovery anyway.
- If `rosdep install` in `postCreateCommand` fails on first build, that's
  expected when `src/` is empty — it's harmless and will start finding
  real dependencies once you add packages.
- You only need "Rebuild Container" (not just reopen) when you change
  `Dockerfile` or `devcontainer.json` — e.g. adding a new apt/pip package.
  Editing your own ROS2 source files never requires a rebuild.


## ROS 2 CLI Command Reference

### Nodes
| Command | Description |
|---|---|
| `ros2 node list` | List all running nodes |
| `ros2 node info <node_name>` | Show a node's subscriptions, publications, services, actions |

### Topics
| Command | Description |
|---|---|
| `ros2 topic list` | List active topics |
| `ros2 topic list -t` | List active topics with message types |
| `ros2 topic echo <topic_name>` | Print messages as they arrive |
| `ros2 topic info <topic_name>` | Show type, publisher/subscriber counts |
| `ros2 topic hz <topic_name>` | Measure publish rate |
| `ros2 topic bw <topic_name>` | Measure bandwidth |
| `ros2 topic pub <topic_name> <msg_type> '<args>'` | Publish manually (`--once` for single, `-r <rate>` to repeat) |
| `ros2 topic type <topic_name>` | Show the message type |

### Services
| Command | Description |
|---|---|
| `ros2 service list` | List active services |
| `ros2 service type <service_name>` | Show a service's type |
| `ros2 service call <service_name> <srv_type> '<args>'` | Call a service manually |
| `ros2 service find <type_name>` | Find services of a given type |

### Actions
| Command | Description |
|---|---|
| `ros2 action list` | List active actions |
| `ros2 action info <action_name>` | Show clients/servers for an action |
| `ros2 action send_goal <action_name> <action_type> '<args>'` | Send a goal manually (`--feedback` to stream feedback) |

### Parameters
| Command | Description |
|---|---|
| `ros2 param list` | List a node's parameters (or all nodes if no arg) |
| `ros2 param get <node_name> <param_name>` | Read a parameter's value |
| `ros2 param set <node_name> <param_name> <value>` | Set a parameter |
| `ros2 param dump <node_name>` | Dump all params to YAML |
| `ros2 param load <node_name> <file>` | Load params from a YAML file |

### Interfaces
| Command | Description |
|---|---|
| `ros2 interface list` | List all available msg/srv/action types |
| `ros2 interface show <type>` | Show the fields of a specific type (e.g. `std_msgs/msg/String`) |

### Packages
| Command | Description |
|---|---|
| `ros2 pkg list` | List all installed packages |
| `ros2 pkg create` | Scaffold a new package |
| `ros2 pkg executables <package_name>` | List runnable executables in a package |
| `ros2 pkg prefix <package_name>` | Show a package's install path |

### Running Things
| Command | Description |
|---|---|
| `ros2 run <package> <executable>` | Run a single node |
| `ros2 launch <package> <launch_file>` | Run a launch file |
| `ros2 launch <package> <launch_file> arg:=value` | Run a launch file with arguments |

### Bags
| Command | Description |
|---|---|
| `ros2 bag record <topic_name>` (or `-a`) | Record topic(s) to a bag file |
| `ros2 bag play <bag_file>` | Replay a bag |
| `ros2 bag info <bag_file>` | Inspect a bag's contents |

### Diagnostics
| Command | Description |
|---|---|
| `ros2 doctor` | Check environment/setup for common issues |
| `ros2 wtf` | Alias for `ros2 doctor`, with report |