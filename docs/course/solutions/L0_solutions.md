# Lecture 0 — Solutions

### 0.1 [S] TF tree of the SLAM configuration

**Model answer.** With `use_aruco:=false slam:=true` (and the default `fuse_slam:=true`):

| Edge | Publisher | Rate |
|---|---|---|
| `map → odom` | `state_estimator_global` (global UKF) | 50 Hz |
| `odom → base_link` | `state_estimator` (odometry UKF) | 50 Hz |
| `base_link → imu_link` | `static_transform_publisher` `base_to_imu_tf` | static |
| `base_link → oak_*` camera and IMU frames | static publishers from `saurcon_nav/launch/oak_sim.launch.py` | static |

RTAB-Map publishes **no** transform here (its `publish_tf` is off because the global UKF owns
`map → odom`). Strong answers note this, and verify the rates with `ros2 run tf2_ros tf2_monitor`.

**Rubric.** Tree correct (4); each dynamic edge attributed to the right node (3); rates measured,
not guessed (2); RTAB-Map's absence explained (1).

### 0.2 [T] `/ctrl_output`

Produced by the state machine (`saurcon_rc/src/state_machine.cpp`, a 30 ms timer); consumed by the
ESP32 on the car and by `sim_saurcon_rc` in simulation. `sim_saurcon_rc` forwards `/ctrl_output` to
Gazebo's `cmd_vel` **only in RUN states**; on leaving a RUN state it publishes one explicit zero
twist. Outside RUN states the state machine itself publishes a stop every 30 ms.

**Why explicit zeros are safer than silence.** A velocity plugin, like a motor controller, holds its
last command until a new one arrives. Silence therefore preserves whatever was last sent, possibly
full throttle; an explicit zero overwrites it. Repeated zeros also keep downstream liveness monitors
satisfied with a *deliberate* stop, so "stopped" and "link lost" stay distinguishable (Lecture 5 §4,
rule 3).

### 0.3 [T] Why the rear axle

At the rear axle the velocity is along the heading (no-slip constraint), so the kinematic model has
no sideslip term (1.2). A point a distance $l_r$ ahead (the centre of mass) moves on a circle of
radius $\sqrt{\rho^2 + l_r^2}$ about the same ICR, with speed
$v_{cg} = v\sqrt{1 + (l_r\tan\delta/L)^2}$ at sideslip angle
$\beta = \arctan(l_r\tan\delta/L)$ to the heading [Kong15]. The difference matters wherever a
controller or estimator equates "velocity direction" with "heading": pure pursuit (9.2) is derived
at the rear axle, odometry integrates speed along the heading (3.6), and ground-truth comparisons
must convert the model origin (0.127 m ahead of `base_link`) to the rear axle (Lecture 7 §1). At
$\delta = 0.4$ rad and $l_r = 0.127$ m, $\beta \approx 0.21$ rad, which is not negligible.

### 0.4 [T] Camera transform

See the lecture's answer. Checks a grader should apply: the columns of ${}^{B}\mathbf C_{C}$ are the
optical axes expressed in the body frame (optical $x$ = body $-y$, optical $y$ = body $-z$, optical
$z$ = body $x$); $\det = +1$; and ${}^{B}T_{C}\,{}^{C}T_{B} = I$.

### 0.5 [T] `odom` vs `map` for remembered landmarks

See the lecture's answer. Full credit also requires the quantitative point: over a 5 s memory the
odometry drift is millimetres (Lecture 3 §7: 0.08–0.18 m RMS over four 47 m laps), whereas a loop
closure can move `map` by decimetres in one step.
