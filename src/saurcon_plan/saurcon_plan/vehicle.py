"""SAURCON car parameters shared by the planner, its ROS node and the MuJoCo environments.

Fitted to the Gazebo car (2026-11-12; docs/course/01_vehicle_modelling_and_sysid.md).
"""
import numpy as np

WHEELBASE = 0.254         # m, rear axle (base_link) to front axle
STEER_MAX = 0.786         # rad, road-wheel steering limit
V_MAX = 12.0              # m/s, largest speed command (also the RL action scale)
CTRL_DT = 0.05            # s, control rate 20 Hz

# Steering slew limit: the car's MG90S micro servo turns ~60 deg in 0.1 s; through the linkage
# take ~8 rad/s at the road wheels. Applied identically in MuJoCo and the ROS node.
STEER_RATE_MAX = 8.0      # rad/s


def slew_steer(prev_norm, target_norm, dt=CTRL_DT):
    """Rate-limit a normalised steering command (-1..1) like the servo."""
    step = STEER_RATE_MAX * dt / STEER_MAX
    return float(np.clip(target_norm, prev_norm - step, prev_norm + step))
