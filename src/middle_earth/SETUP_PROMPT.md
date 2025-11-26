# Gazebo Simulation Setup Prompt

This prompt will recreate the complete RC Ackermann vehicle simulation with ArUco marker localization.

## Complete Setup Prompt

```
I'd like to build a Gazebo simulation in the middle_earth folder with the following specifications:

1. **RC Ackermann Vehicle:**
   - RC car size: 0.4m long, 0.2m wide
   - Wheelbase: 0.3m, track width: 0.26m
   - Wheel radius: 0.03m
   - Ackermann steering on front wheels
   - Rear wheel drive
   - Control via /cmd_vel topic
   - Physics: DART engine with proper friction
   - Wheel damping: 0.01, chassis friction: 0.01

2. **Environment:**
   - Basement-sized room: 12m x 10m
   - Cherry wood floor (amber: 0.4,0.2,0.1, diffuse: 0.6,0.3,0.15)
   - 2.5m high walls
   - Good lighting for camera visibility

3. **ArUco Markers for Localization:**
   - 10 markers total, evenly spaced in an oval pattern
   - Size: 6" x 6" (0.1524m x 0.1524m)
   - Height: 12" (0.3048m) above ground
   - Vertical orientation (orthogonal to ground)
   - Each marker oriented to point toward center (0,0)
   - Oval pattern: 4m X-radius, 3m Y-radius
   - Use DICT_4X4_50 ArUco dictionary, IDs 0-9
   - Generate actual ArUco marker textures using OpenCV

4. **Directory Structure:**
   - models/ (vehicle and marker models)
   - worlds/ (basement.world)
   - materials/textures/ (ArUco marker images)
   - config/ (vehicle parameters)
   - scripts/ (teleoperation)
   - launch/, plugins/, meshes/ (for future use)

Please set up the complete simulation with all components working together.
```

## Expected Result

After running this prompt, you should have:

- **Working RC vehicle** with Ackermann steering that responds to `/cmd_vel` commands
- **Basement environment** with cherry wood floor and walls
- **10 ArUco markers** positioned in an oval, all facing the center for optimal localization
- **Generated marker textures** (aruco_0.png through aruco_9.png) using OpenCV
- **Organized folder structure** ready for expansion

## Testing the Simulation

Launch the simulation:
```bash
cd /home/morgoth/middle_earth
gz sim worlds/basement.world
```

Control the vehicle:
```bash
# Drive forward
gz topic -t '/cmd_vel' -m gz.msgs.Twist -p 'linear: {x: 1.0}'

# Turn while driving
gz topic -t '/cmd_vel' -m gz.msgs.Twist -p 'linear: {x: 1.0}, angular: {z: 0.5}'

# Reverse
gz topic -t '/cmd_vel' -m gz.msgs.Twist -p 'linear: {x: -1.0}'
```

## Key Configuration Details

### Vehicle Parameters
- Max velocity: 3.0 m/s
- Max acceleration: 5.0 m/s²
- Steering limit: 0.5 rad (~28.6°)
- Vehicle mass: 2.0 kg
- Wheel mass: 0.3 kg each

### ArUco Marker Positions (Oval Pattern)
Markers are automatically calculated to form an oval (4m × 3m) with each marker's normal vector pointing toward the center (0,0).

### Physics Configuration
- Engine: DART
- Step size: 0.001s
- Gravity: -9.8 m/s²
- Floor friction: μ=1.0
- Wheel friction: μ=1.0
- Joint damping: 0.01 (low for RC car responsiveness)

## Files Created

```
middle_earth/
├── models/
│   ├── rc_ackermann_vehicle/
│   │   ├── model.sdf (full vehicle definition)
│   │   └── model.config
│   └── aruco_marker/
│       ├── model.sdf (6"×6" vertical marker template)
│       ├── model.config
│       └── materials/textures/ (symlinks to ArUco images)
├── worlds/
│   └── basement.world (main simulation world)
├── materials/
│   └── textures/
│       ├── aruco_0.png
│       ├── aruco_1.png
│       └── ... (through aruco_19.png)
├── config/
│   └── vehicle_params.yaml
└── scripts/
    └── teleop_vehicle.py
```

## Next Steps

To extend this simulation, you could add:
1. Camera sensor on the RC vehicle for ArUco detection
2. ROS 2 bridge for integration with Nav2/SLAM
3. Custom control algorithms
4. Additional obstacles or track features
5. IMU and odometry sensors
6. Recording and playback capabilities
