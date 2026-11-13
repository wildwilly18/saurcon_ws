"""Cone-vision racing in MuJoCo: the policy sees only the cones in its camera view.

No map, no localization, no centreline in the observation. Each step the policy
gets its own speed, yaw rate, steering and previous action, plus the K nearest
cones from a short memory: every cone detected in the last MEMORY_S seconds, kept
in the odometry frame and re-expressed in the current base_link (x, y) with its
age. The camera sees only +/-33 deg, so in the racetrack's 2 m bends the cones to
follow are beside the car and out of view; without memory the policy goes blind
mid-bend (found when the first version ran wide in Gazebo). This is not a map:
it forgets everything older than a couple of seconds.

Training uses a *simulated detector* (fast): cones inside the OAK-D's horizontal
field of view and range, with range-dependent noise and a miss rate measured from
the real detector on Gazebo frames (MISS_PROB). Validation
can instead render the MuJoCo camera and run the real detector on the pixels
(`saurcon_rl.cone_drive`). The simulator still uses the track centreline to
score progress and to end the episode when the car leaves the cone corridor;
that is the referee, not an input to the policy.
"""
import math

import gymnasium as gym
import numpy as np

from saurcon_plan.memory import ConeMemory
from saurcon_plan.vehicle import STEER_RATE_MAX, slew_steer  # noqa: F401 (re-exported)

from .env import CRASH_PENALTY, CTRL_DT, STEER_MAX
from .mujoco_env import MujocoRaceEnv

CAMERA_X = 0.219                  # camera ahead of base_link (m), as on the car
HALF_FOV = 0.58                   # rad: 1.204 rad horizontal FOV minus a cone width at the edge
MIN_RANGE, MAX_RANGE = 0.35, 6.5  # m: nearer cones fall below the image; farther are < 5 px tall
# Miss probability by range (m), measured on Gazebo frames with the ground-plane detector
# (docs/course notebook 08, 40 frames, 2026-11-12): near gate cones sit at the edge of the
# field of view or below the image; far cones are only a few pixels tall. Replaces the first,
# hand-set model 0.05 + 0.15 (r / 6.5)^2. Rough (small sample): refit over full laps.
MISS_RANGES = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
MISS_PROB = np.array([0.90, 0.75, 0.25, 0.12, 0.45, 0.80, 0.90])
STALL_SPEED, STALL_S, STALL_GRACE_S = 0.3, 2.0, 1.0   # m/s, s stopped, s after start
K_CONES = 12
MEMORY_S = 2.0                    # seconds a detected cone is remembered after its last sighting
CONE_OBS_DIM = 5 + 4 * K_CONES
# Smooth driving (2026-11-13). The first cone policies steered bang-bang: the command changed
# ~8 deg every 50 ms step and flipped sign on a third of the steps, which the old penalty
# 0.02*|da|^2 barely charged, and in Gazebo the car weaved +/-0.4-1 m on the straights.
STEER_RATE_W = 0.5       # per step, times (change of the normalised steering action)^2
YAW_EXCESS_W = 0.05      # per step, times (yaw rate - speed * track curvature)^2, (rad/s)^2
# Steering slew limit (MG90S servo, saurcon_plan.vehicle): applied identically in MuJoCo and
# in the planner's ROS node.

def smooth_penalty(steer_norm, prev_steer_norm, yaw_rate, v, curvature):
    """Reward penalty for unsmooth driving (on top of the base 0.02*|da|^2)."""
    return (STEER_RATE_W * (steer_norm - prev_steer_norm) ** 2
            + YAW_EXCESS_W * (yaw_rate - v * curvature) ** 2)


def encode(points_base_xy, v, yaw_rate, steer, prev_action, ages=None):
    """Policy observation from cone positions in the base_link frame (and their ages in seconds).
    Shared with the rendered-pixel path (cone_drive)."""
    pts = np.asarray(points_base_xy, float).reshape(-1, 2)
    ages = np.zeros(len(pts)) if ages is None else np.asarray(ages, float)
    if len(pts):
        order = np.argsort(np.hypot(pts[:, 0], pts[:, 1]))[:K_CONES]
        pts, ages = pts[order], ages[order]
    feat = np.zeros((K_CONES, 4), np.float32)
    feat[:len(pts), :2] = pts / 10.0
    feat[:len(pts), 2] = 1.0
    feat[:len(pts), 3] = ages / MEMORY_S
    head = [v / 10.0, yaw_rate / 5.0, steer / STEER_MAX, prev_action[0], prev_action[1]]
    return np.concatenate([head, feat.ravel()]).astype(np.float32)


def visible_cones(cones_xy, x, y, yaw, rng=None, noise=True):
    """Simulated detector: cones the camera would report, in the base_link frame."""
    c, s = math.cos(yaw), math.sin(yaw)
    dx = cones_xy[:, 0] - (x + CAMERA_X * c)
    dy = cones_xy[:, 1] - (y + CAMERA_X * s)
    bx, by = c * dx + s * dy, -s * dx + c * dy            # camera-centred, x forward
    r = np.hypot(bx, by)
    vis = (bx > 0) & (np.abs(np.arctan2(by, bx)) < HALF_FOV) & (r > MIN_RANGE) & (r < MAX_RANGE)
    bx, by, r = bx[vis], by[vis], r[vis]
    if noise and rng is not None and len(r):
        keep = rng.random(len(r)) > np.interp(r, MISS_RANGES, MISS_PROB)        # measured miss rate
        bx, by, r = bx[keep], by[keep], r[keep]
        bearing = np.arctan2(by, bx) + rng.normal(0, 0.004, len(r))
        r = r * (1 + rng.normal(0, 0.02, len(r))) + rng.normal(0, 0.006, len(r)) * r ** 2
        bx, by = r * np.cos(bearing), r * np.sin(bearing)
    return np.column_stack([bx + CAMERA_X, by])


class MujocoConeEnv(MujocoRaceEnv):
    def __init__(self, *args, detector_noise=True, **kwargs):
        # Detector misses and noise stay on even when randomize=False (evaluation): the
        # policy is trained on a detector that misses most near and far cones, and showing it
        # every cone is a situation it never saw -- the first evaluations crashed for that reason.
        super().__init__(*args, **kwargs)
        self.detector_noise = detector_noise
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, (CONE_OBS_DIM,), np.float32)

    def reset(self, seed=None, options=None):
        self.memory = ConeMemory(horizon=MEMORY_S)
        self.slow_steps = 0
        return super().reset(seed=seed, options=options)

    def step(self, action):
        a = np.clip(np.asarray(action, np.float32), -1, 1).copy()
        prev_steer = float(self.prev_action[1])
        a[1] = slew_steer(prev_steer, float(a[1]), CTRL_DT)
        obs, reward, terminated, truncated, info = super().step(a)
        reward -= smooth_penalty(float(a[1]), prev_steer, self.state[4], self.v, float(self.track.curvature[self.i]))
        # Stalling ends the episode like a crash. With frequent missed detections, parking
        # (zero reward, no crash) became a stable trap during training; a per-step time
        # penalty would instead make crashing early look better than driving carefully.
        self.slow_steps = self.slow_steps + 1 if abs(self.v) < STALL_SPEED else 0
        if not terminated and self.t > STALL_GRACE_S and self.slow_steps * CTRL_DT >= STALL_S:
            terminated = True; reward -= CRASH_PENALTY; info['stalled'] = True
        return obs, reward, terminated, truncated, info

    def _obs(self):
        x, y, yaw, v, yr, steer = self.history[-1 - self.delay]
        r = self.np_random
        pts = visible_cones(self.track.cones, x, y, yaw, r, noise=self.detector_noise)
        c, s = math.cos(yaw), math.sin(yaw)
        self.memory.update(np.column_stack([x + c * pts[:, 0] - s * pts[:, 1], y + s * pts[:, 0] + c * pts[:, 1]]), self.t)
        rel, ages = self.memory.relative(x, y, yaw, self.t)
        if self.randomize:
            v *= 1 + r.normal(0, 0.02)
        return encode(rel, v, yr, steer, self.prev_action, ages)
