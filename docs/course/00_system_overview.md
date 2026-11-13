# Lecture 0 — System Overview

*Reading:* [REP105]; [Kabzan20], introduction and system overview (the architecture of a full autonomous racing system).

## Outcomes

After this lecture you can (i) draw SAURCON's data flow from sensors to wheels and name the
node and package responsible for each step; (ii) explain the `map`, `odom` and `base_link`
frames and why two different estimators publish transforms between them; (iii) launch the
simulator in its main configurations and diagnose a stack that does not run.

## 1. The platform

SAURCON is a 1:10 scale Ackermann-steered car: rear-wheel drive, front-wheel steering by an
MG90S servo, wheelbase $L = 0.254$ m, track $T_w = 0.165$ m, wheel radius 33 mm, steering
limit $\delta_{\max} = 0.786$ rad. An ESP32 runs the motor and servo and reads the wheel
encoders and IMU; it talks to ROS 2 over micro-ROS on a serial link. A Raspberry Pi 4 runs
ROS 2 Jazzy. The exteroceptive sensor is a Luxonis **OAK-D Lite**: a colour camera and a
stereo pair that computes depth on the device.

The course uses three models of this car, of increasing fidelity and decreasing speed:

| Model | Fidelity | Speed | Used for |
|---|---|---|---|
| Kinematic bicycle (L1) | kinematics, actuator rates, a friction rule | ~5,800 steps/s/core | fast RL experiments |
| MuJoCo (L8) | rigid bodies, tyre contact, weight transfer | ~1,000 steps/s/core | RL training and evaluation |
| Gazebo Harmonic | physics + rendered camera, IMU, full ROS 2 stack | real time | the driving stack, SLAM, validation |

Gazebo provides three worlds: `racetrack.world` (a 47.6 m stadium circuit in a warehouse,
2.2 m gates with extra gates in the bends, 108 cones), `basement.world` (a 25.2 m oval,
1.2 m gates, 72 cones) and `feature_warehouse.world` (a 64.3 m irregular loop with dense
0.65 m gate spacing and textured surroundings for visual SLAM).

## 2. Architecture

```
             ┌──────────── wheel speed, IMU (/saurcon/odom, /saurcon/imu)
ESP32 /      │
sim_saurcon_rc ─┤
             │       ┌───────────────────┐   TF odom→base_link   ┌───────────┐
             └──────►│ odometry UKF       ├──────────────────────►│ RTAB-Map  │◄── OAK-D RGB + depth
                     │ (saurcon_nav)      │                        │ (SLAM)    │
                     └───────────────────┘                        └─────┬─────┘
             ┌──────────── wheel speed, IMU                              │ newest map node
             │       ┌───────────────────┐                               │
             └──────►│ global UKF         │◄──────────────────────────────┘
                     │ (saurcon_nav)      ├── /saurcon/nav_state (map frame, 50 Hz), TF map→odom
                     └───────────────────┘

OAK-D RGB + depth ─► cone follower (saurcon_plan) ── /auto_cmd ──► state machine (saurcon_rc)
     ▲ TF odom→base_link, /saurcon/odom_nav                        │   (STANDBY / RUN_CONTROL /
                     joystick (/joy) ─────────────────────────────►│    RUN_AUTONOMOUS / FAULT)
                                                                   ▼
                                                       /ctrl_output ──► ESP32 / Gazebo car
```

Three design decisions shape everything that follows.

1. **The planner needs no map.** The car drives with the classical cone follower (L9):
   camera and odometry in, `/auto_cmd` out. Localization and mapping (L3–L4) run alongside
   and produce a map and a globally consistent pose, but driving does not depend on them.
   This keeps the safety-critical loop short and its failure modes few.
2. **Estimation is split in two.** An odometry filter owns the smooth `odom` frame; a
   second, global filter fuses SLAM and owns the `map` correction. L4 §5 explains why one
   filter cannot do both.
3. **Learning happens in simulation.** Reinforcement learning (L6, L8) is trained and
   evaluated in MuJoCo (`saurcon_rl`, no ROS). L6 §7 presents the evidence for keeping it
   out of the driving stack, and the bar a learned policy would have to clear to get in.

| Package | Role | Lectures |
|---|---|---|
| `middle_earth` | Gazebo worlds, car and sensor models, cones | 1, 2 |
| `saurcon_perception` | ArUco detection and marker localization (legacy) | 2 |
| `saurcon_nav` | Unscented Kalman filter, RTAB-Map launch, map cleaning | 3, 4 |
| `saurcon_rc` | State machine, joystick handling, simulated ESP32, simulation launch | 5 |
| `saurcon_plan` | Cone detector, cone memory, track geometry, classical follower and its node, cone mapper | 9 |
| `saurcon_rl` | RL in simulation: bicycle and MuJoCo environments, PPO, evaluation, system identification | 6, 8 |
| `scripts/sim_eval` | Scripted runs, logging, scoring, plots, race videos | 7, 9 |

## 3. Coordinate frames

ROS follows [REP105]:

- **`base_link`** $\{B\}$ is rigid with the car. SAURCON puts it at the centre of the
  **rear axle**, the reference point at which the kinematic bicycle model has no sideslip
  (L1 §2).
- **`odom`** $\{O\}$ is world-fixed and *continuous*: the pose in it never jumps, but it
  drifts. Controllers that need smooth motion use it.
- **`map`** $\{M\}$ is world-fixed and *globally consistent*, but the pose in it may jump
  when a correction arrives (a loop closure, a marker sighting).

TF stores a tree, so each frame has exactly one parent: `map → odom → base_link → {camera,
imu}`. The odometry filter publishes ${}^{O}T_{B}$; the localization layer publishes
${}^{M}T_{O}$, chosen so that ${}^{M}T_{O}\,{}^{O}T_{B}$ equals the corrected pose. Two nodes
publishing the same edge make the tree inconsistent in ways that look like noise (L3 §7).

## 4. Running the system

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
# Simulation with ArUco localization (the original configuration)
ros2 launch saurcon_rc full_sim_saurcon.launch.py
# Map the track with RTAB-Map (no markers; Ctrl-C saves the database)
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false slam:=true \
    database_path:=$PWD/maps/track.db
# Drive from the camera with the classical cone follower (no map needed)
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false cone_follower:=true
# ... while localizing in a saved map
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false slam:=true \
    mode:=localization initial_pose:="0 0 0 0 0 0" database_path:=$PWD/maps/track.db \
    cone_follower:=true
# Scripted 3-lap race with logs, chase camera and the follower's waypoints
scripts/sim_eval/cone_race.sh my_run 3
```

Hold the controller's *view* button for 2 s to hand control to the follower; hold *menu* or
*view* for 2 s to take it back. Useful arguments: `headless:=true`, `record:=false`,
`world:=<file>`, `fuse_slam:=false`, `follower_speed_limit:=<m/s>`,
`cone_mapping:=rtab|truth|both`, `cone_debug_csv:=<file>`.

**Debugging checklist.** (1) `ros2 node list`: is every node up, and is any name duplicated
(a stale process)? (2) `ros2 topic hz <topic>`: does data flow at the expected rate?
(3) `ros2 run tf2_ros tf2_echo map base_link`: does the TF chain resolve? (4) `ros2 topic
echo /saurcon/state`: which mode is the car in? (5) `ps`: are orphaned `gz sim` (`ruby`)
processes from an earlier run still alive? They share topics and silently corrupt results
(L7 §3).

## Summary

- The driving loop is camera → cone follower → state machine → actuators; it needs only
  odometry, not a map.
- Two estimators split `odom → base_link` (smooth) from `map → odom` (correct).
- Three simulators trade fidelity for speed; learning lives in the fast ones.

## Problems

**0.1** [S] ★ Launch the SLAM configuration and draw the TF tree
(`ros2 run tf2_tools view_frames`). Label each edge with the node that publishes it and its
rate.

**0.2** [T] ★ Find where `/ctrl_output` is produced and consumed. What does `sim_saurcon_rc`
publish on it in `STANDBY`, and why is that safer than publishing nothing?

**0.3** [T] ★★ Explain why `base_link` is placed at the rear axle rather than the centre of
mass. Write the velocity of the centre of mass in terms of $v$, $\delta$ and the distance
$l_r$ from the rear axle, and show where the difference matters.

**0.4** [T] ★★ The camera is mounted 0.219 m ahead of and 0.05 m above `base_link`. Write
${}^{B}T_{C}$ including the body-to-optical rotation, and its inverse.

**0.5** [T] ★★ The follower uses `odom`, not `map`. Argue from the definitions in §3 why a
controller that steers to remembered landmarks should prefer the continuous frame, and
describe what would happen at a loop closure if it used `map`.

### Answers to selected problems

**0.4** With the optical frame $x$ right, $y$ down, $z$ forward, the rotation from optical
to body is ${}^{B}\mathbf C_{C} = \begin{bmatrix}0&0&1\\-1&0&0\\0&-1&0\end{bmatrix}$ and
${}^{B}\mathbf t_{C} = (0.219, 0, 0.05)^\top$; the inverse is
${}^{C}\mathbf C_{B} = {}^{B}\mathbf C_{C}^{\top}$, ${}^{C}\mathbf t_{B} = -{}^{C}\mathbf
C_{B}\,{}^{B}\mathbf t_{C} = (0, 0.05, -0.219)^\top$.

**0.5** A loop closure changes ${}^{M}T_{O}$ in one step; every remembered cone expressed in
`map` would jump with it while the car has not moved, and the follower would steer toward
where the cones *used* to be. In `odom` the remembered cones and the car share the same drift,
which over the few seconds of memory is millimetres.
