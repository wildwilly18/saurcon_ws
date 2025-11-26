# Middle Earth Gazebo Simulation

A Gazebo simulation environment featuring an RC-sized Ackermann steering vehicle in a basement-sized world.

## Structure

```
middle_earth/
├── models/
│   └── rc_ackermann_vehicle/    # RC car model with Ackermann steering
├── worlds/
│   └── basement.world           # 6m x 8m basement environment
├── launch/
│   └── basement_sim.launch      # Main launch file
├── config/
│   └── vehicle_params.yaml      # Configurable vehicle parameters
├── scripts/
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
```bash
# Ensure ROS and Gazebo are installed
sudo apt-get install ros-noetic-gazebo-ros-pkgs ros-noetic-gazebo-ros-control
```

### Launch Simulation
```bash
# Source ROS workspace
source /opt/ros/noetic/setup.bash

# Launch the simulation
roslaunch middle_earth basement_sim.launch
```

### Control the Vehicle

#### Option 1: Keyboard Teleoperation
```bash
# Make script executable
chmod +x scripts/teleop_vehicle.py

# Run teleop
./scripts/teleop_vehicle.py
```

**Controls:**
- `w/s`: Forward/Backward
- `a/d`: Steer Left/Right
- `Space`: Stop
- `q`: Quit

#### Option 2: ROS Command Line
```bash
# Publish velocity commands directly
rostopic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 0.5
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.2"
```

## Topics

- `/cmd_vel` - Command velocity (Twist)
- `/odom` - Odometry data
- `/gazebo/model_states` - Model states

## Notes

- The Ackermann plugin automatically handles the steering geometry
- Front wheels steer independently to maintain proper Ackermann angles
- Rear wheels provide the drive torque
- Physics runs at 1000 Hz for smooth simulation
