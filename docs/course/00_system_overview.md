# Chapter 0 — System Overview

## Learning objectives

By the end of this chapter you should be able to:

- Draw the SAURCON data flow from sensors to wheels and name the ROS 2 node that owns each step.
- Explain the `map`, `odom` and `base_link` frames and why two different nodes publish transforms between them.
- Launch the simulator in its main configurations and know where to look when something does not work.

## 1. The platform

SAURCON is a 1:10 scale Ackermann-steered RC car: rear-wheel drive, front-wheel
steering, 0.254 m wheelbase, 0.165 m track, 33 mm wheel radius, and a ±0.786 rad
steering limit. An ESP32 runs the motors and reads the wheel encoders and IMU; it
talks to ROS 2 through **micro-ROS** over a serial link. A Raspberry Pi 4 runs ROS
2 Jazzy. The perception sensor is a **Luxonis OAK-D Lite**: a colour camera plus
a stereo pair that computes depth on the device, and an onboard IMU.

Everything in this course can be done in **Gazebo Harmonic**. Two worlds are
provided: `racetrack.world` (a 47.6 m stadium-shaped circuit in a warehouse) and
`basement.world` (a 25.2 m oval). Both are lined with gates of 1:10 traffic cones:
2.2 m wide on the racetrack, with an extra gate between gates in each bend (108
cones), and 1.2 m wide on the basement oval (72 cones).

## 2. The data flow

```
             ┌──────────── wheel speed, IMU (/saurcon/odom, /saurcon/imu)
ESP32 /      │
sim_saurcon_rc ─┤
             │       ┌───────────────────┐   TF odom→base_link   ┌───────────┐
             └──────►│ odometry UKF       ├──────────────────────►│ RTAB-Map  │◄── OAK-D Lite RGB + depth
                     │ (saurcon_nav)      │                        │ (SLAM)    │
                     └───────────────────┘                        └─────┬─────┘
             ┌──────────── wheel speed, IMU                              │ pose of newest map node
             │       ┌───────────────────┐                               │
             └──────►│ global UKF         │◄──────────────────────────────┘
                     │ (saurcon_nav)      ├── /saurcon/nav_state (map frame, 50 Hz), TF map→odom
                     └─────────┬─────────┘
                               ▼
                 race policy (saurcon_rl) ── /auto_cmd ──► state machine (saurcon_rc)
                                                           │   (STANDBY / RUN_CONTROL /
                     joystick (/joy) ─────────────────────►│    RUN_AUTONOMOUS / FAULT)
                                                           ▼
                                               /ctrl_output ──► ESP32 / Gazebo car
```

The **map-based** race policy above needs a global pose (RTAB-Map or ArUco). The
**cone-vision** pipeline of chapter 9 needs neither: it drives from the camera and
odometry alone, and RTAB-Map may run beside it only to build a map.

```
OAK-D RGB + depth ─► cone_policy_node: detector ─► cone memory (odom frame) ─► classical follower
                                ▲ TF odom→base_link, /saurcon/odom_nav           or learned policy
                                                                                      │
                                                         /auto_cmd ◄──────────────────┘
```

| Package | Role | Chapter |
|---|---|---|
| `middle_earth` | Gazebo worlds, car and sensor models, cones | 1, 2 |
| `saurcon_perception` | ArUco detection and marker-based localization (legacy) | 2 |
| `saurcon_nav` | Unscented Kalman Filter, RTAB-Map launch | 3, 4 |
| `saurcon_rc` | State machine, joystick handling, simulated ESP32 | 5 |
| `saurcon_rl` | RL environments (bicycle, MuJoCo, Gazebo), training, policy nodes, cone detector, classical cone follower | 6, 8, 9 |
| `scripts/sim_eval` | Scripted laps, cone races, logging, scoring, plots, race videos | 7, 9 |

## 3. Coordinate frames

ROS follows [REP-105](https://www.ros.org/reps/rep-0105.html):

- **`base_link`** is rigidly attached to the car. Here it is the centre of the rear
  axle, which is also the reference point of the kinematic bicycle model (chapter 1).
- **`odom`** is a world-fixed frame in which the car's pose is *continuous*: it never
  jumps, but it drifts. Controllers that need smooth motion use it.
- **`map`** is a world-fixed frame in which the pose is *globally correct* but may
  jump when a correction arrives (a loop closure, a marker sighting).

TF stores a tree, so each frame has exactly one parent. The chain is
`map → odom → base_link → {camera, imu}`. The odometry filter owns
`odom → base_link`; the localization layer owns `map → odom`, chosen so that the
composition equals the corrected pose. Chapter 4 explains why the split matters,
and chapter 3 shows what happens when two nodes accidentally publish the same link.

## 4. Running the system

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
# Simulation with ArUco localization (the original configuration)
ros2 launch saurcon_rc full_sim_saurcon.launch.py
# SLAM: map the track (drive it, then Ctrl-C to save the database)
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false slam:=true \
    database_path:=$PWD/maps/track.db
# Localize in a saved map and race with a trained policy
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false slam:=true \
    mode:=localization initial_pose:="0 0 0 0 0 0" database_path:=$PWD/maps/race.db \
    policy_model:=rl_runs/ppo_v1/best_model.zip
# Drive from the camera alone with the classical cone follower (no map needed)
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false \
    cone_policy_model:=classical
# Scripted 3-lap cone race with logs, chase camera and the follower's waypoints
scripts/sim_eval/cone_race.sh classical my_run 3
```

Useful launch arguments: `headless:=true` (no Gazebo window), `record:=false`
(no rosbag), `world:=<file>`, `fuse_slam:=false` (let RTAB-Map own `map→odom`),
`policy_map_origin:="x y yaw"` (world pose of an RTAB-Map frame started away from the
spawn), `cone_mapping:=rtab|truth|both` (build a cone map), `cone_debug_csv:=<file>`
(log the classical follower's state every step).

The map policy only launches with a localization source (`use_aruco:=true`, or
`slam:=true` with `fuse_slam:=true`); odometry-only combinations are refused.

### Debugging checklist

1. `ros2 node list` — is every node up? Duplicated names mean a stale process.
2. `ros2 topic hz <topic>` — is data flowing at the expected rate?
3. `ros2 run tf2_ros tf2_echo map base_link` — does the TF chain resolve?
4. `ros2 topic echo /saurcon/state` — what state is the car in?
5. Check `ps` for orphaned `gz sim` (`ruby`) or node processes from earlier runs —
   they share topics and silently corrupt results (chapter 7).

## Exercises

1. ★ Launch the SLAM configuration and draw the TF tree (`ros2 run tf2_tools view_frames`). Which node publishes each edge?
2. ★ Find where `/ctrl_output` is produced and consumed. What does `sim_saurcon_rc` do with it in `STANDBY`?
3. ★★ Explain why `base_link` is placed at the rear axle rather than the centre of mass. (Hint: chapter 1, the bicycle model.)
4. ★★ The camera is mounted 0.219 m ahead of and 0.05 m above `base_link`. Write the homogeneous transform and its inverse.
