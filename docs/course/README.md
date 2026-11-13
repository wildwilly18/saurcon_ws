# Autonomous Racing with SAURCON — Course Notes

An upper-level engineering course built around one real system: a 1:10 scale
Ackermann RC car that localizes with an RGB-D camera, fuses its sensors with an
Unscented Kalman Filter, builds and localizes in a map with RTAB-Map, and races
around a cone track, from a map with a reinforcement-learning policy or from the
camera alone with a learned or classical controller. Every concept is taught
twice: once from first principles in a notebook, once as it appears in the code.

**Prerequisites.** Linear algebra, probability (Gaussians, covariance),
introductory control and dynamics, Python, and basic C++. ROS 2 familiarity
helps but chapter 0 covers what is needed.

## Modules

| # | Chapter | Notebook | Core ideas |
|---|---|---|---|
| 0 | [System overview](00_system_overview.md) | — | ROS 2 graph, frames (REP-105), how to run everything |
| 1 | [Vehicle modelling & system identification](01_vehicle_modelling_and_sysid.md) | [01](notebooks/01_bicycle_model_and_sysid.ipynb) | Ackermann geometry, kinematic bicycle model, grip limit, fitting a model to data |
| 2 | [Sensors & perception](02_sensors_and_perception.md) | [02](notebooks/02_camera_geometry_and_pnp.ipynb) | IMU and wheel odometry, pinhole cameras, stereo depth error, ArUco + PnP, pose ambiguity |
| 3 | [State estimation with the UKF](03_state_estimation_ukf.md) | [03](notebooks/03_unscented_kalman_filter.ipynb) | Sigma points, prediction/update, gating, bias, consistency, latency compensation |
| 4 | [SLAM & localization](04_slam_and_localization.md) | [04](notebooks/04_pose_graph_slam.ipynb) | Pose graphs, loop closures, false closures, map→odom at a common time, dual-filter fusion, occupancy grids, landmark maps |
| 5 | [Vehicle software & safety](05_vehicle_software_and_safety.md) | — | State machines, dead-man switches, heartbeats, autonomy hand-off, input-freshness checks |
| 6 | [Reinforcement learning for racing](06_reinforcement_learning_racing.md) | [05](notebooks/05_rl_racing.ipynb) | MDP design, reward shaping, PPO and GAE, domain randomization, sim-to-sim transfer |
| 7 | [Experimental method](07_experimental_method.md) | — | Ground truth, alignment, metrics, run isolation, honest reporting |
| 8 | [Physics simulation with MuJoCo](08_mujoco_simulation.md) | [06](notebooks/06_mujoco_fundamentals.ipynb), [07](notebooks/07_mujoco_sim_to_sim.ipynb) | MJCF, soft contact and friction cones, modelling a car, calibrating against Gazebo, predicting failures |
| 9 | [Perception-driven racing](09_perception_driven_racing.md) | [08](notebooks/08_cone_perception.ipynb) | Cone detection and ranging, object-level perception for training, short-term memory, validating on pixels, fitting a detector error model, smooth-driving rewards, training in Gazebo, a classical cone follower as the baseline, stopping on stale inputs |

A suggested 15-week schedule: weeks 1–2 chapters 0–1, 3–4 chapter 2,
5–7 chapter 3, 8–9 chapter 4, 10 chapter 5, 11–12 chapter 6, 13–14 chapter 8
(MuJoCo) and chapter 9 (perception-driven racing), 15 chapter 7 and project
presentations. Chapters 8 and 9 can also be taught together as a stand-alone
three-week module after chapters 1, 2 and 6.

## Running the notebooks

```bash
./scripts/setup.sh                       # once: ROS 2, Gazebo, and the .venv-rl environment
source /opt/ros/jazzy/setup.bash && source install/setup.bash
.venv-rl/bin/pip install jupyterlab       # once
.venv-rl/bin/jupyter lab docs/course/notebooks
```

Pick the **SAURCON (.venv-rl)** kernel. Notebooks 06–07 need MuJoCo (installed
by `setup.sh`) and render offscreen with `MUJOCO_GL=egl` (set automatically; use
`osmesa` on a machine without a GPU). Notebooks 1–4 need only NumPy,
Matplotlib, SciPy and OpenCV; notebook 5 imports `saurcon_rl` from the workspace
(source `install/setup.bash` first) and uses a trained policy if one exists in
`rl_runs/`. The notebooks are committed with their outputs, so they can be read
without running them.

## How the chapters are organised

Each chapter has **learning objectives**, the **theory**, **how SAURCON does it**
(with file paths), **case studies** taken from bugs actually found while building
this system, and **exercises** graded (★ to ★★★). The case studies matter: most
of the hard lessons in robotics come from systems that *almost* work.

## Project ideas

1. Add a gyro-bias state to the UKF and show it learns the bias from RTAB-Map.
2. Make the RL policy robust to a 2× slower localization rate.
3. Replace pure-pursuit mapping laps with a policy that explores for loop closures.
4. Identify the real car (chapter 1 method) and retrain; compare sim and real laps.
5. Train from camera images instead of the state estimate; compare sample efficiency.
6. Port the MuJoCo environment to MJX and train on the GPU (chapter 8, exercise 5).
7. Beat the classical cone follower with learning: a residual policy on top of it, or RL on its planned path (chapter 9, exercises 10–11).
8. Make the RTAB-Map cone map move with loop closures and measure its precision (chapter 4, exercise 5).

## Tests

The safety and geometry fixes in chapters 4, 5 and 9 have regression tests that need
no simulator:

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
PYTHONPATH=src/saurcon_rl:$PYTHONPATH .venv-rl/bin/python -m pytest -q src/saurcon_rl/test scripts/sim_eval/tests
python3 -m pytest -q src/saurcon_rc/test
colcon test --packages-select saurcon_nav && colcon test-result --verbose
```
