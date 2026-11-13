Saurcon_WS is the ROS network code that implements for the SAURCON RC vehicle.

## Setup

Targets Ubuntu 24.04 with ROS 2 Jazzy and Gazebo Harmonic.

```bash
git clone --recurse-submodules <this repo> saurcon_ws
cd saurcon_ws
./scripts/setup.sh
```

`scripts/setup.sh` adds the ROS 2 apt repository, installs ROS 2 Jazzy, the
build tools and Gazebo, fetches the micro-ROS agent submodules, installs the
remaining package dependencies with `rosdep`, and builds the workspace with
`colcon`. It asks for `sudo`.

## Running

In each new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

| Command | What it starts |
| --- | --- |
| `ros2 launch saurcon_rc full_sim_saurcon.launch.py` | Gazebo racetrack world, bridges, joystick, state machine, ArUco detection/localization, state estimator, rosbag recording to `bags/` |
| `ros2 launch saurcon_rc sim_saurcon.launch.py` | Joystick, state machine and simulated RC node, without Gazebo |
| `ros2 launch saurcon_rc saurcon.launch.py` | On-vehicle: state machine and micro-ROS agent on `/dev/ttyUSB0` |
| `ros2 launch saurcon_rc bringup.launch.py` | Joystick, control interface and micro-ROS agent on `/dev/ttyUSB0` |

The joystick nodes expect a gamepad (e.g. an Xbox controller) to be connected.
The racetrack world downloads its warehouse models from Gazebo Fuel on first
launch, so the first start needs an internet connection and takes a while.

Rebuild after code changes with `colcon build --symlink-install`.

RTAB-Map simulation mapping/localization, OAK-D Lite sensor topics and repeatable
lap evaluation are described in [docs/RTABMAP_USAGE.md](docs/RTABMAP_USAGE.md).
ArUco remains selectable until the measured replacement meets its baseline.
