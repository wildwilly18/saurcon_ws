# saurcon_rl — racing policies: map-based RL, and cone vision (learned or classical)

Drives the SAURCON car around the cone raceway as fast as possible, two ways:

```
map-based:   fused UKF (/saurcon/nav_state, map frame) ─► policy_node ─────────┐
cone vision: OAK-D RGB + depth ─► cone_policy_node (detector, cone memory,     ├─► /auto_cmd ─► state machine
             odometry) ─► classical follower or learned cone policy ──────────┘    (RUN_AUTONOMOUS) ─► car
```

The course chapters explain both in depth: map-based RL in
`docs/course/06_reinforcement_learning_racing.md`, cone vision and the classical
follower in `docs/course/09_perception_driven_racing.md`.

## Pieces

| File | Purpose |
|---|---|
| `saurcon_rl/track.py` | Track centreline, gates and drivable corridor, read from a world file's cone gates |
| `saurcon_rl/env.py` | Fast Gymnasium environment: bicycle model fitted to the Gazebo car, randomised |
| `saurcon_rl/mujoco_env.py`, `mujoco_model.py` | MuJoCo environment and car model (styled after the real car) |
| `saurcon_rl/cones.py` | Cone detector (colour, blobs, depth/ground/size ranging) |
| `saurcon_rl/cone_env.py` | Cone-vision environment: simulated detector, cone memory, servo slew, smooth-driving reward |
| `saurcon_rl/gazebo_cone_env.py` | The same task in lock-step headless Gazebo with the real detector (`--env gazebo_cones`) |
| `saurcon_rl/cone_follower.py` | Classical cone follower: Delaunay gate midpoints, pure pursuit, curvature speed profile |
| `saurcon_rl/cone_drive.py` | Drive a cone policy or the follower in MuJoCo from rendered pixels, with video |
| `saurcon_rl/train.py` | PPO training (Stable-Baselines3), with lap-time evaluation |
| `saurcon_rl/policy_node.py` | ROS 2 node that drives with a trained map-based policy |
| `saurcon_rl/cone_policy_node.py` | ROS 2 node that drives from the camera (`model:=<zip>` or `model:=classical`) |
| `saurcon_rl/cone_mapper_node.py` | Cone map from ground truth or RTAB-Map poses |
| `saurcon_rl/sysid.py` | Measures the Gazebo car's dynamics on an empty floor (`config/sysid.world`) |
| `test/` | Regression tests: input watchdogs, follower geometry |

**Car model** (fitted to Gazebo, 2026-11-12): 3.8 m/s² acceleration and
4.0 m/s² braking (the drive plugin's ramps, set just under tyre grip),
0.254 m wheelbase, 0.786 rad steering limit, ~0.2 s steering lag, and a
friction circle of ~10 m/s² with braking counted 1.5× (rear-only brakes).
Outside the circle the episode ends as a spin. Training randomises these, plus
pose noise (≤5 cm, ≤0.9°) and sensing delay (≤60 ms).

**Observation** (31 values): speed, yaw rate, steering, previous action, offset
and heading error from the centreline, and 12 centreline points 0.5–15 m ahead
in the car frame. **Action**: speed command (0–12 m/s) and steering angle.
**Reward**: metres of progress per 50 ms step; leaving the cone corridor or
exceeding grip ends the episode with a penalty.

Training uses the racetrack (both directions, 70%) and the basement oval (both
directions, 30%).

## MuJoCo environment

`saurcon_rl/mujoco_env.py` (`MujocoRaceEnv`) has the same interface as `RaceEnv`
but simulates the car as rigid bodies with tyre contacts (`mujoco_model.py`
generates the MJCF), so weight transfer, wheel spin and brake-induced oversteer
come from physics. Tyre friction 1.4 is calibrated against Gazebo's grip
(`python -m saurcon_rl.sysid --mujoco <dir>` and `python -m saurcon_rl.sysid_compare`).
It runs ~1,000 control steps/s per core (bicycle model ~5,800).

MuJoCo predicted a Gazebo failure the bicycle model missed: a policy fine-tuned
with the friction-circle rule lapped cleanly in the bicycle model but spun in
MuJoCo and in Gazebo. Train in MuJoCo with `--env mujoco`. Background and the
calibration are in `docs/course/08_mujoco_simulation.md`.

## Use

Needs the `.venv-rl` virtual environment from `scripts/setup.sh`.

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
# Train (about an hour for 20 M steps on 12 cores)
.venv-rl/bin/python -m saurcon_rl.train --out rl_runs/ppo_v1 --steps 20000000
# Watch: tensorboard --logdir rl_runs   (race/flying_lap_s)

# Race in Gazebo with the full localization loop (needs a saved map, e.g. maps/race.db)
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false slam:=true \
  mode:=localization initial_pose:="0 0 0 0 0 0" database_path:=$PWD/maps/race.db \
  policy_model:=rl_runs/ppo_v1/best_model.zip
# The policy needs a map pose: slam:=true with fuse_slam:=true (map frame; its world pose is
# policy_map_origin, default "-1.127 0 0", the racetrack spawn) or use_aruco:=true (world frame).
# Odometry-only modes are rejected at launch. If /saurcon/nav_state stops for 0.25 s
# (state_timeout) the policy publishes zero commands until it resumes.
# Then hold the controller's view button for 2 s (STANDBY -> RUN_AUTONOMOUS).
# Hold menu or view for 2 s to take back control. The joystick is a dead-man
# switch: losing it faults the car; losing /auto_cmd for 0.25 s stops it.
```

Scripted full-loop races: `DRIVER=race_driver.py RACE_LAPS=3 scripts/sim_eval/runsim.sh ...`
(see `scripts/sim_eval/race_driver.py`).

`policy_node` converts the pose into the Gazebo world frame with `map_origin`, which
the launch file sets from the localization mode (`policy_map_origin`). On the real car
the track would be defined in the map frame directly.

## Cone vision

```bash
# Classical follower in Gazebo, 3 laps, logs + chase camera + waypoints, then a video
scripts/sim_eval/cone_race.sh classical my_run 3
.venv-rl/bin/python scripts/sim_eval/make_race_video.py evaluation/cones_gz/my_run my_run.mp4
# ... with RTAB-Map mapping in the marker-free world (video gets the live map panel)
scripts/sim_eval/cone_race.sh classical my_slam_run 3 \
  world:=$PWD/evaluation/worlds/no_markers.world slam:=true cone_mapping:=rtab
# In MuJoCo from rendered pixels
.venv-rl/bin/python -m saurcon_rl.cone_drive --model classical --laps 2 --video out.mp4
# Train a cone policy in MuJoCo; fine-tune in lock-step Gazebo (about 37 steps/s per server)
.venv-rl/bin/python -m saurcon_rl.train --env mujoco_cones --out rl_runs/cones_x --steps 20000000
.venv-rl/bin/python -m saurcon_rl.train --env gazebo_cones --out rl_runs/cones_gz_x \
  --resume rl_runs/cones_x/best_model.zip --envs 4 --steps 3000000
```

The cone node stops (zero `/auto_cmd`) if its newest image was captured more than
0.3 s ago, odometry is older than 0.25 s, or the `odom → base_link` transform is
missing or older than 0.25 s; it pairs each colour image with the depth image of the
same stamp. Results so far: the classical follower laps the racetrack in Gazebo in
about 12.4–13.3 s; the best learned cone policy in about 31.8 s
(`docs/course/09_perception_driven_racing.md`, section 11).

## Tests

```bash
source /opt/ros/jazzy/setup.bash
PYTHONPATH=src/saurcon_rl:$PYTHONPATH .venv-rl/bin/python -m pytest -q src/saurcon_rl/test
```
