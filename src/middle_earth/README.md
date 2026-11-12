# Middle Earth Gazebo Simulation

A Gazebo simulation environment featuring an RC-sized Ackermann steering vehicle in a basement-sized world.

## Structure

```
middle_earth/
├── models/
│   └── rc_ackermann_vehicle/    # RC car model with Ackermann steering
├── worlds/
│   └── basement.world           # 6m x 8m basement environment
├── config/
│   ├── vehicle_params.yaml      # Reference vehicle parameters
│   └── bridge_config.yaml       # ROS 2 <-> Gazebo topic bridge
├── scripts/
│   ├── start_simulation.sh      # Gazebo + bridge
│   ├── start_bridge.sh          # Bridge only
│   └── teleop_vehicle.py        # Keyboard teleoperation
├── plugins/                      # Custom Gazebo plugins
├── meshes/                       # 3D mesh files
└── materials/                    # Textures and materials
```

## Vehicle Specifications

- **Type**: RC Ackermann steering vehicle
- **Size**: ~0.4m long x 0.2m wide (1:10 RC scale)
- **Mass**: 2.0 kg
- **Wheelbase**: 0.3m
- **Max Speed**: 2.0 m/s
- **Max Steering Angle**: ±0.6 radians (~34°)

## World Specifications

- **Size**: 8m x 6m (typical basement dimensions)
- **Wall Height**: 2.5m
- **Floor**: Concrete-like surface

## Configuration

Edit `config/vehicle_params.yaml` to adjust vehicle dimensions:

- **Small RC (1:18)**: Multiply dimensions by 0.7
- **Standard RC (1:10)**: Use default values
- **Large RC (1:8)**: Multiply dimensions by 1.3

## Usage

### Prerequisites

ROS 2 Jazzy with Gazebo Harmonic (`ros-jazzy-ros-gz`). The workspace-level
`scripts/setup.sh` installs both.

```bash
source /opt/ros/jazzy/setup.bash
```

### Launch Simulation

```bash
# Basement world + ROS 2 bridge
./scripts/start_simulation.sh
```

The full stack (racetrack world, state machine, ArUco localisation, state
estimator) is launched from the workspace with
`ros2 launch saurcon_rc full_sim_saurcon.launch.py`.

### Control the Vehicle

#### Option 1: Keyboard Teleoperation
```bash
python3 scripts/teleop_vehicle.py
```

**Controls:**
- `w/s`: Forward/Backward
- `a/d`: Steer Left/Right
- `Space`: Stop
- `q`: Quit

#### Option 2: ROS Command Line
```bash
ros2 topic pub /model/rc_ackermann_vehicle/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.2}}"
```

## Topics

Bridged to ROS 2 by `config/bridge_config.yaml`:

- `/model/rc_ackermann_vehicle/cmd_vel` - Command velocity (Twist, ROS → Gazebo)
- `/model/rc_ackermann_vehicle/odom` - Wheel odometry
- `/model/rc_ackermann_vehicle/imu` - IMU
- `/model/rc_ackermann_vehicle/joint_states` - Wheel and steering joints
- `/camera/image`, `/camera/depth_image`, `/camera/camera_info` - RGBD camera
- `/clock` - Simulation time

## Notes

- The Ackermann plugin automatically handles the steering geometry
- Front wheels steer independently to maintain proper Ackermann angles
- Rear wheels provide the drive torque
- Physics runs at 1000 Hz for smooth simulation
