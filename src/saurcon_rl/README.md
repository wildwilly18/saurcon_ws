# saurcon_rl — reinforcement learning in simulation (MuJoCo)

Trains and evaluates racing policies for the SAURCON car **in simulation only**: a fast
bicycle model and a MuJoCo rigid-body model of the car, for two tasks:

- **map-based racing**: the policy sees the stored track centreline ahead of the car;
- **cone vision**: the policy sees only the cones a simulated (or rendered-and-detected)
  OAK-D camera reports.

There are no ROS nodes here. The car and Gazebo are driven by the classical cone follower in
`saurcon_plan`, which this package also uses as the baseline in MuJoCo, together with the
shared detector, cone memory, track geometry and car parameters. (The ROS 2 nodes that ran
learned policies in Gazebo, and the lock-step Gazebo training environment, were removed on
2026-11-13; their results are recorded in `docs/course/06_reinforcement_learning_racing.md`
and `09_perception_driven_racing.md`.)

## Pieces

| File | Purpose |
|---|---|
| `saurcon_rl/env.py` | Fast Gymnasium environment (`RaceEnv`): bicycle model fitted to the Gazebo car, randomised; the base of the MuJoCo environments |
| `saurcon_rl/mujoco_model.py` | MJCF generator: the car (styled after the real one) and the cone track |
| `saurcon_rl/mujoco_env.py` | `MujocoRaceEnv`: the same task with rigid bodies and tyre contacts |
| `saurcon_rl/cone_env.py` | `MujocoConeEnv`: cone-vision task, simulated detector (measured miss rates), 2 s cone memory, servo slew, smooth-driving reward |
| `saurcon_rl/cone_drive.py` | Drive a trained cone policy or the classical follower (`--model classical`) in MuJoCo, from rendered pixels through the real detector or from the simulated detector; video |
| `saurcon_rl/train.py` | PPO training (Stable-Baselines3) with lap-time evaluation: `--env bicycle\|mujoco\|mujoco_cones` |
| `saurcon_rl/sysid.py`, `sysid_compare.py` | Identification drive of the Gazebo car (gz-transport, no ROS) and of the MuJoCo model, and their comparison; used to calibrate MuJoCo |
| `test/` | Smoke tests: environment API, finite steps, the follower driving in MuJoCo |

**Car model** (fitted to Gazebo, 2026-11-12): 3.8 m/s² acceleration and
4.0 m/s² braking, 0.254 m wheelbase, 0.786 rad steering limit, ~0.2 s steering lag, and a
friction circle of ~10 m/s² with braking counted 1.5× (rear-only brakes). Outside the circle
the episode ends as a spin. Training randomises these, plus pose noise (≤5 cm, ≤0.9°) and
sensing delay (≤60 ms). Shared constants live in `saurcon_plan/vehicle.py`.

**Map-based observation** (31 values): speed, yaw rate, steering, previous action, offset
and heading error from the centreline, and 12 centreline points 0.5–15 m ahead in the car
frame. **Cone observation** (53): speed, yaw rate, steering, previous action and the 12
nearest remembered cones (forward, left, present, age). **Action**: speed command
(0–12 m/s) and steering angle. **Reward**: metres of progress per 50 ms step (cone task: minus
a steering-rate and yaw-excess penalty); leaving the cone corridor or exceeding grip ends the
episode with a penalty.

## MuJoCo

`MujocoRaceEnv` has the same interface as `RaceEnv` but simulates the car as rigid bodies with
tyre contacts, so weight transfer, wheel spin and brake-induced oversteer come from physics.
Tyre friction 1.4 is calibrated against Gazebo's grip (`sysid --mujoco` and `sysid_compare`).
It runs ~1,000 control steps/s per core (bicycle model ~5,800). MuJoCo predicted a Gazebo spin
the bicycle model missed; see `docs/course/08_mujoco_simulation.md`.

## Use

Needs the `.venv-rl` virtual environment from `scripts/setup.sh`, and both packages on the
Python path (sourcing `install/setup.bash` after `colcon build` does this too):

```bash
export PYTHONPATH=$PWD/src/saurcon_plan:$PWD/src/saurcon_rl:$PYTHONPATH MUJOCO_GL=egl
# Train (about an hour for 20 M steps on 12 cores); watch with tensorboard --logdir rl_runs
.venv-rl/bin/python -m saurcon_rl.train --env mujoco --out rl_runs/ppo_mj1 --steps 20000000
.venv-rl/bin/python -m saurcon_rl.train --env mujoco_cones --out rl_runs/cones_x --steps 20000000
# Evaluate in MuJoCo: a cone policy, or the classical follower, from rendered pixels, with video
.venv-rl/bin/python -m saurcon_rl.cone_drive --model rl_runs/cones_x/best_model.zip --laps 2 --video out.mp4
.venv-rl/bin/python -m saurcon_rl.cone_drive --model classical --laps 2 --video classical.mp4
# Calibrate: identification drive of the MuJoCo car
.venv-rl/bin/python -m saurcon_rl.sysid --mujoco evaluation/sysid_mujoco
```

## Tests

```bash
PYTHONPATH=src/saurcon_plan:src/saurcon_rl:$PYTHONPATH MUJOCO_GL=egl \
    .venv-rl/bin/python -m pytest -q src/saurcon_rl/test
```
