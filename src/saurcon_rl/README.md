# saurcon_rl — reinforcement-learning racing policy

Trains a policy that drives the SAURCON car around the cone raceway as fast as
possible, and runs it on the car through the normal stack.

```
fused UKF (/saurcon/nav_state, map frame) ─► policy_node ─► /auto_cmd ─► state machine
                                                             (RUN_AUTONOMOUS) ─► /ctrl_output ─► car
```

## Pieces

| File | Purpose |
|---|---|
| `saurcon_rl/track.py` | Track centreline, gates and drivable corridor, read from a world file's cone gates |
| `saurcon_rl/env.py` | Fast Gymnasium environment: bicycle model fitted to the Gazebo car, randomised |
| `saurcon_rl/train.py` | PPO training (Stable-Baselines3), with lap-time evaluation |
| `saurcon_rl/policy_node.py` | ROS 2 node that drives with a trained policy |
| `saurcon_rl/sysid.py` | Measures the Gazebo car's dynamics on an empty floor (`config/sysid.world`) |

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
# Then hold the controller's view button for 2 s (STANDBY -> RUN_AUTONOMOUS).
# Hold menu or view for 2 s to take back control. The joystick is a dead-man
# switch: losing it faults the car; losing /auto_cmd for 0.25 s stops it.
```

Scripted full-loop races: `DRIVER=race_driver.py RACE_LAPS=3 scripts/sim_eval/runsim.sh ...`
(see `scripts/sim_eval/race_driver.py`).

`policy_node` assumes the map frame's origin is the Gazebo spawn pose
(`map_origin` parameter, default `[-1.127, 0, 0]`), which holds when the map was
built starting from the spawn. On the real car the track would be defined in
the map frame directly.
