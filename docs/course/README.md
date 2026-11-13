# Autonomous Racing Systems
### Estimation, Mapping, Planning and Learning on a 1:10 Scale Car — Graduate Course Notes

## Course description

Autonomous racing compresses the whole robotics stack into a few seconds per lap: the car
must perceive a track it has never mapped, estimate its own motion from imperfect sensors,
localize against a map it builds itself, plan and track a path at the limit of tyre grip,
and do all of it safely when any input can arrive late, wrong or not at all. This course
develops each of those capabilities from first principles and then follows it into a real
system, SAURCON: a 1:10 scale Ackermann car with wheel encoders, an IMU and an OAK-D Lite
RGB-D camera, running ROS 2, a simulated twin in Gazebo, and a rigid-body model in MuJoCo.

Two threads run through the course. The **model thread** asks what a model of the car, a
sensor or the world must capture to be useful, and how to identify, validate and break it.
The **evidence thread** asks how we know a system works: ground truth, metrics, repeated
trials and honest reporting. The course ends by comparing a learned racing policy with a
classical planner on equal terms, and by asking which one deserves to drive.

## Prerequisites

Linear algebra (eigen-decomposition, least squares), probability (multivariate Gaussians,
conditional distributions), introductory control (state space, feedback) and dynamics,
fluent Python, and reading knowledge of C++. ROS 2 is introduced in Lecture 0; no prior
robotics course is assumed, but students who have taken one will find Lectures 1–3 a
fast-paced review with new depth.

## Learning outcomes

On completing the course, a student will be able to:

1. **Model** an Ackermann vehicle kinematically and dynamically, state each model's domain
   of validity, and identify its parameters from designed experiments (L1).
2. **Derive** the measurement models of wheel odometry, gyroscopes, pinhole and stereo
   cameras, and propagate their errors to the quantities a controller uses (L2).
3. **Design, implement and validate** a nonlinear Bayesian filter, including gating,
   bias estimation, latency compensation and consistency testing (L3).
4. **Formulate** SLAM as sparse nonlinear least squares, explain loop-closure acceptance as
   hypothesis testing, and configure a production SLAM system and its occupancy maps (L4).
5. **Engineer** safety mechanisms (mode logic, watchdogs, input-validity checks) and test
   them without hardware (L5).
6. **Derive and apply** policy-gradient methods (GAE, PPO), design rewards and
   randomisation for transfer, and evaluate learned policies with statistical care (L6, L8).
7. **Plan** at the limits of the vehicle: build a path from perceived landmarks, track it
   with pure pursuit and plan a feasible speed profile (L9).
8. **Run experiments** that support claims: ground-truth alignment, trajectory metrics,
   isolation, confidence intervals on reliability, and complete reporting (L7).

## Lectures

| # | Lecture | Notebook | Core ideas |
|---|---|---|---|
| 0 | [System overview](00_system_overview.md) | — | Architecture, ROS 2 graph, frames (REP-105), the simulators |
| 1 | [Vehicle modelling and system identification](01_vehicle_modelling_and_sysid.md) | [01](notebooks/01_bicycle_model_and_sysid.ipynb) | Ackermann geometry, kinematic and dynamic bicycle models, understeer, friction circle, minimum-time speed profiles, least-squares identification |
| 2 | [Sensors and measurement models](02_sensors_and_perception.md) | [02](notebooks/02_camera_geometry_and_pnp.ipynb) | Odometry and gyro error models, pinhole and stereo geometry, error propagation, PnP and planar ambiguity |
| 3 | [Nonlinear state estimation](03_state_estimation_ukf.md) | [03](notebooks/03_unscented_kalman_filter.ipynb) | Bayes filter, Kalman filter derivation, unscented transform, gating, NEES/NIS consistency, bias, latency |
| 4 | [SLAM and localization](04_slam_and_localization.md) | [04](notebooks/04_pose_graph_slam.ipynb) | Factor graphs, Gauss–Newton, loop-closure testing, map→odom, occupancy grids, landmark maps |
| 5 | [Safety-critical vehicle software](05_vehicle_software_and_safety.md) | — | Mode logic, hazard analysis, watchdogs vs. validity checks, testing with fakes |
| 6 | [Reinforcement learning for racing](06_reinforcement_learning_racing.md) | [05](notebooks/05_rl_racing.ipynb) | MDPs, policy-gradient theorem, GAE, PPO, reward shaping, domain randomisation, evaluation |
| 7 | [Experimental method](07_experimental_method.md) | — | Ground truth, alignment, ATE/RPE, isolation, statistics of small samples, reporting |
| 8 | [Physics simulation with MuJoCo](08_mujoco_simulation.md) | [06](notebooks/06_mujoco_fundamentals.ipynb), [07](notebooks/07_mujoco_sim_to_sim.ipynb) | Generalised coordinates, soft contact as convex optimisation, friction cones, calibration, sim-to-sim |
| 9 | [Perception-driven racing: planning from cones](09_perception_driven_racing.md) | [08](notebooks/08_cone_perception.ipynb), [09](notebooks/09_classical_follower.ipynb) | Object-level perception, partial observability, Delaunay centrelines, pure pursuit, speed planning, learned vs. classical |

Supporting material: [notation](notation.md) (read first), [references](references.md), 13 figures in
`figures/` regenerated from the code by `figures/make_figures.py`, and, for instructors, a
[solutions manual](solutions/README.md) with reference results computed by
`solutions/reference_results.py`.

## Schedule (14 weeks; two 80-minute lectures and one 2-hour lab per week)

| Week | Lectures | Required reading | Lab | Due |
|---|---|---|---|---|
| 1 | L0, L1 §1–3 | [Rajamani12] ch. 2–3; [Kong15] | Launch the simulator; drive a lap; draw the TF tree | — |
| 2 | L1 §4–6 | [Ljung99] ch. 1, 7 (skim) | Identify the Gazebo car (notebook 01) | PS1 out |
| 3 | L2 §1–3 | [Hartley04] ch. 6; [Szeliski22] §12.1 | Camera intrinsics and stereo error (notebook 02) | |
| 4 | L2 §4–5, L3 §1–2 | [Thrun05] ch. 2–3 | PnP and the planar ambiguity | PS1 |
| 5 | L3 §3–6 | [Julier04]; [BarShalom01] §5.4 | Build and tune a UKF (notebook 03) | PS2 out |
| 6 | L3 §7, L4 §1–3 | [Grisetti10]; [Cadena16] | Pose-graph SLAM from scratch (notebook 04) | Project proposal |
| 7 | L4 §4–7 | [Labbe19]; [Elfes89] | Map the warehouse with RTAB-Map | PS2 |
| 8 | L5 | [Leveson11] ch. 1–2; [Koopman16] | Break the car safely: fault injection with fake clocks | PS3 out |
| 9 | L7 | [Zhang18]; [Henderson18] | Score a run: alignment, ATE, reliability intervals | |
| 10 | L6 §1–4 | [Sutton18] ch. 13; [Schulman16]; [Schulman17] | Train a racing policy (notebook 05) | PS3 |
| 11 | L6 §5–8, L8 §1–3 | [Tobin17]; [Todorov12] | MuJoCo fundamentals (notebook 06) | PS4 out |
| 12 | L8 §4–7 | [Todorov14] | Calibrate MuJoCo against Gazebo (notebook 07) | Project milestone |
| 13 | L9 | [Coulter92]; [Kabzan20]; [Kaufmann23] | Cone perception and the classical follower (notebooks 08–09) | PS4 |
| 14 | Project presentations | — | — | Final report |

## Assessment

| Component | Weight | Notes |
|---|---|---|
| Problem sets (4) | 30% | Theory and computation drawn from the problems at the end of two to three lectures. Typeset solutions; code in a runnable notebook. |
| Labs (12) | 15% | Short structured reports: what was measured, how, the number with its uncertainty. |
| Project | 45% | Proposal 5%, milestone 10%, final report and code 25%, presentation 5%. |
| Participation | 10% | Lecture discussion and code review of a peer's lab. |

Problems are tagged **[T]** theory, **[C]** computation (notebook or script), **[S]**
simulation (Gazebo or MuJoCo run), and graded ★ (one sitting), ★★ (a few hours), ★★★ (a
mini-project). Answers to selected problems appear at the end of each lecture.

## Project

Teams of two pose a question that the SAURCON stack can answer with evidence, and answer it.
The deliverable is an 8-page report in conference format with a reproducible artifact
(scripts that regenerate every figure). Strong projects change one thing, measure its
effect over repeated trials, and explain the mechanism. Examples:

1. Make the RTAB-Map cone map move with loop closures and measure the change in precision (L4, problem 4.6).
2. Replace the follower's centreline with a minimum-curvature racing line computed from the drivable map, and measure lap time and reliability (L9).
3. Train a residual RL policy on top of the classical follower in MuJoCo and test whether it beats the follower without losing robustness (L6, L9).
4. Add a gyro-bias state to the UKF and show it is learned from RTAB-Map fixes alone (L3).
5. Identify the physical car with the method of L1 and quantify the sim-to-real gap of each simulator.
6. Port `MujocoRaceEnv` to MJX and measure training throughput on a GPU (L8).

## Software

```bash
./scripts/setup.sh                        # once: ROS 2 Jazzy, Gazebo Harmonic, .venv-rl
source /opt/ros/jazzy/setup.bash && source install/setup.bash
.venv-rl/bin/pip install jupyterlab       # once
.venv-rl/bin/jupyter lab docs/course/notebooks
```

Pick the **SAURCON (.venv-rl)** kernel. Notebooks 01–04 need only NumPy, Matplotlib, SciPy
and OpenCV; notebooks 05–09 import `saurcon_rl` and `saurcon_plan` from the workspace (they
add both `src/` folders to the path), and MuJoCo renders offscreen with `MUJOCO_GL=egl`
(`osmesa` without a GPU). Notebooks are committed with their outputs.

Regression tests (no simulator needed except for the MuJoCo smoke tests):

```bash
PYTHONPATH=src/saurcon_plan:$PYTHONPATH python3 -m pytest -q src/saurcon_plan/test src/saurcon_rc/test
PYTHONPATH=src/saurcon_plan:src/saurcon_rl:$PYTHONPATH MUJOCO_GL=egl \
    .venv-rl/bin/python -m pytest -q src/saurcon_rl/test scripts/sim_eval/tests
colcon test --packages-select saurcon_nav && colcon test-result --verbose
```

## How the lectures are written

Each lecture states its **outcomes**, develops the **theory** with derivations a student can
reproduce, gives the **algorithm**, and then shows **how SAURCON implements it**, with file
paths. The **From the lab** sections are case studies from building this system: each is a
real failure, the measurement that exposed it, and the general lesson. They are the part of
the course that textbooks cannot provide; most hard lessons in robotics come from systems
that *almost* work.
