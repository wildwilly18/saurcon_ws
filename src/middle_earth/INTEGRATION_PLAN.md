# SAURCON Integration Plan: Gazebo Simulation → Real Hardware

## Overview
Adapt the existing SAURCON ROS 2 workspace to work with the Gazebo simulation, creating a seamless development/testing environment before deploying to real hardware.

---

## Current System Architecture

### **Gazebo Simulation (Current State)**
- **Environment**: Basement world (12m x 10m)
- **Vehicle**: RC Ackermann model (0.4m x 0.2m)
  - Wheelbase: 0.3m
  - Track width: 0.26m
  - Max velocity: 3.0 m/s
- **Sensors**:
  - IMU: `/imu` (sensor_msgs/Imu) @ 100Hz
  - RGBD Camera: `/camera/image`, `/camera/depth`, `/camera/points`, `/camera/camera_info` @ 30Hz
- **Control**: `/cmd_vel` (geometry_msgs/Twist)
- **Localization**: 12 ArUco markers (6"x6") in oval pattern (4.5m x 3.5m)

### **Real Hardware (SAURCON_RC)**
- **Microcontroller**: ESP32 with micro-ROS
- **Actuators**:
  - Servo (steering)
  - ESC-driven BLDC motor (throttle)
- **Sensors**:
  - MPU6050 IMU
  - 6-pole hall sensors (motor velocity/direction)
  - Servo position feedback
- **Communication**: micro-ROS agent over serial (USB, 921600 baud)

### **ROS 2 Control Stack (SAURCON_WS)**
- **Package**: `control_rc`
- **Main Nodes**:
  - `saurcon_main`: State machine/control logic
  - `ctrl_interface`: Joy → control command translator
- **Input**: `joy_node` (joystick input)
- **Launch Files**:
  - `saurcon.launch.py`: Full system with micro-ROS agent
  - `bringup.launch.py`: Simplified bringup

---

## Integration Goals

### **Phase 1: Simulation-Only Development** ✅
**Goal**: Develop and test control algorithms in Gazebo before hardware deployment

**What We'll Do**:
1. ✅ Create Gazebo simulation matching RC car specs (DONE)
2. ✅ Add IMU and camera sensors (DONE)
3. ✅ Set up ArUco marker track for localization (DONE)
4. ✅ Bridge Gazebo ↔ ROS 2 (DONE)
5. **Adapt `control_rc` package for simulation**:
   - Modify `saurcon_main` to subscribe to `/cmd_vel` (Gazebo) instead of micro-ROS topics
   - Add ArUco detection node using `/camera/image`
   - Create localization node using ArUco markers
   - Test control algorithms with simulated IMU data

### **Phase 2: Hardware-Simulation Parity**
**Goal**: Make code work identically in both environments

**What We'll Do**:
1. **Create abstraction layer** for hardware/simulation switching:
   ```python
   # Launch parameter: sim_mode=true/false
   if sim_mode:
       cmd_topic = "/cmd_vel"  # Gazebo
   else:
       cmd_topic = "/rc/cmd"   # micro-ROS
   ```
2. **Unified sensor interface**:
   - IMU: Use `/imu` topic in both (map micro-ROS → standard topic)
   - Camera: Simulation only (real hardware may add later)
3. **Control command mapping**:
   - Gazebo: `Twist.linear.x` (m/s), `Twist.angular.z` (rad/s)
   - Hardware: Servo angle, ESC PWM
   - Create translator node for hardware mode

### **Phase 3: Dual-Mode Operation**
**Goal**: Single codebase, switchable via launch parameter

**What We'll Do**:
1. **Unified launch file** (`saurcon_unified.launch.py`):
   ```python
   def generate_launch_description():
       sim_mode = LaunchConfiguration('sim_mode', default='false')
       
       nodes = [
           Node(package='control_rc', executable='saurcon_main', ...),
           Node(package='control_rc', executable='ctrl_interface', ...),
           Node(package='joy', executable='joy_node', ...),
       ]
       
       # Conditional: Simulation or Hardware
       sim_nodes = [
           ExecuteProcess(cmd=['gz', 'sim', 'basement.world']),
           Node(package='ros_gz_bridge', ...),
       ]
       
       hw_nodes = [
           ExecuteProcess(cmd=['micro_ros_agent', 'serial', ...]),
       ]
       
       return LaunchDescription([
           DeclareLaunchArgument('sim_mode', default_value='false'),
           *nodes,
           *ConditionalNodes(sim_mode, sim_nodes, hw_nodes)
       ])
   ```

2. **Testing protocol**:
   - Develop in sim → Test in sim → Deploy to hardware
   - Same joystick control in both modes
   - Same state machine behavior

---

## Technical Implementation Details

### **Step 1: Adapt `control_rc` Package**
**Files to Modify**:
- `src/control_rc/src/saurcon_main.cpp`:
  - Add parameter for `sim_mode`
  - Switch between `/cmd_vel` (sim) and micro-ROS topics (hw)
  - Handle simulated vs. real sensor data
  
- `src/control_rc/launch/saurcon.launch.py`:
  - Add `sim_mode` argument
  - Conditionally launch micro-ROS agent OR Gazebo + bridge
  
**New Nodes to Create**:
- `aruco_detector` (Python):
  - Subscribe: `/camera/image`
  - Publish: `/aruco/detections` (marker IDs, poses)
  - Use `cv2.aruco` library
  
- `localization` (Python/C++):
  - Subscribe: `/aruco/detections`, `/imu`
  - Publish: `/odom` or `/pose`
  - Estimate vehicle position on track

### **Step 2: Create Simulation-Specific Launch**
**File**: `src/control_rc/launch/saurcon_sim.launch.py`
```python
def generate_launch_description():
    return LaunchDescription([
        # Start Gazebo simulation
        ExecuteProcess(
            cmd=['/home/morgoth/middle_earth/scripts/start_simulation.sh'],
            output='screen'
        ),
        
        # Control nodes
        Node(package='control_rc', executable='saurcon_main',
             parameters=[{'sim_mode': True}]),
        Node(package='control_rc', executable='ctrl_interface'),
        Node(package='joy', executable='joy_node'),
        
        # Vision/localization
        Node(package='control_rc', executable='aruco_detector'),
        Node(package='control_rc', executable='localization'),
    ])
```

### **Step 3: Command Mapping**
**Simulation → Hardware Translation**:

| Simulation (Gazebo)          | Hardware (ESP32 micro-ROS)        |
|------------------------------|-----------------------------------|
| `/cmd_vel` (Twist)           | `/rc/steering`, `/rc/throttle`    |
| `linear.x`: 0.0-3.0 m/s      | ESC PWM: 1000-2000 µs             |
| `angular.z`: -0.5-0.5 rad    | Servo angle: -30° to +30°         |
| `/imu` (standard)            | `/mpu6050/imu` (micro-ROS)        |

**Translator Node** (for hardware mode):
```python
def cmd_vel_callback(msg):
    # Map linear velocity to ESC
    throttle_pwm = map_range(msg.linear.x, 0, 3.0, 1500, 2000)
    
    # Map angular velocity to steering
    steering_angle = msg.angular.z * (180/pi)  # rad to deg
    
    pub_throttle.publish(throttle_pwm)
    pub_steering.publish(steering_angle)
```

---

## Directory Structure

```
middle_earth/
├── worlds/
│   └── basement.world           # Gazebo world
├── models/
│   └── rc_ackermann_vehicle/    # Vehicle model
├── scripts/
│   ├── start_simulation.sh      # Launch Gazebo + bridge
│   └── start_bridge.sh          # ROS 2 bridge only
├── config/
│   ├── bridge_config.yaml       # Gazebo ↔ ROS 2 topic mapping
│   └── vehicle_params.yaml      # Vehicle parameters
└── materials/textures/
    └── aruco_*.png              # ArUco marker images

saurcon_ws/
├── src/
│   ├── control_rc/              # Main control package
│   │   ├── src/
│   │   │   ├── saurcon_main.cpp         # State machine (MODIFY)
│   │   │   ├── ctrl_interface.cpp       # Joy interface
│   │   │   ├── aruco_detector.py        # NEW: ArUco detection
│   │   │   └── localization.cpp         # NEW: Position estimation
│   │   ├── launch/
│   │   │   ├── saurcon.launch.py        # Hardware launch (MODIFY)
│   │   │   ├── saurcon_sim.launch.py    # NEW: Simulation launch
│   │   │   └── saurcon_unified.launch.py # NEW: Switchable launch
│   │   └── CMakeLists.txt               # Add new nodes
│   ├── joy/                     # Joystick input (existing)
│   └── micro_ros_agent/         # Hardware communication (existing)
└── install/                     # Built packages
```

---

## Testing Strategy

### **Simulation Testing**:
1. **Manual Control**: Drive using joystick in Gazebo
2. **Sensor Validation**: 
   - View IMU data: `ros2 topic echo /imu`
   - View camera: `rqt_image_view /camera/image`
3. **ArUco Detection**: Verify marker detection as car moves
4. **Localization**: Plot estimated position vs. ground truth

### **Hardware Testing**:
1. **Bench Test**: Vehicle stationary, test servo/motor response
2. **Sensor Validation**: Compare micro-ROS IMU with simulation
3. **Track Test**: Run on actual track with ArUco markers
4. **Performance Compare**: Sim vs. hardware behavior

---

## Next Steps (Priority Order)

1. **Clone `saurcon_ws` into development environment**
   ```bash
   cd /home/morgoth
   git clone https://github.com/wildwilly18/saurcon_ws.git
   cd saurcon_ws
   colcon build
   ```

2. **Create ArUco detector node**
   - File: `src/control_rc/src/aruco_detector.py`
   - Subscribe to `/camera/image`
   - Detect markers using `cv2.aruco`
   - Publish detections with IDs and poses

3. **Modify `saurcon_main.cpp` for simulation mode**
   - Add `sim_mode` parameter
   - Subscribe to `/cmd_vel` when in sim mode
   - Add fallback for missing micro-ROS topics

4. **Create simulation launch file**
   - File: `src/control_rc/launch/saurcon_sim.launch.py`
   - Launch Gazebo simulation
   - Launch control nodes with `sim_mode=true`
   - Launch ArUco detector

5. **Test end-to-end**: Joystick → ROS 2 → Gazebo → Sensors → Localization

---

## Success Criteria

- ✅ Can control simulated vehicle with joystick
- ✅ ArUco markers detected and localization working
- ✅ Same control code runs in simulation and hardware (with parameter switch)
- ✅ Smooth transition from sim testing → hardware deployment
- ✅ Documentation allows other developers to replicate setup

---

## Notes

- **Simulation advantages**: Safe testing, no hardware wear, rapid iteration
- **Hardware differences**: Real world has noise, latency, mechanical imperfections
- **Recommendation**: Develop 80% in simulation, validate/tune 20% on hardware
- **Future**: Add noise models to simulation to better match hardware behavior
