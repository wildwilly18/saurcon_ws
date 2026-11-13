"""Fast raceway environment for training (Gymnasium).

Kinematic bicycle model of the Gazebo car, fitted to the system-identification
drives (2026-11-12):
  acceleration 3.8 m/s^2 and braking 4.0 m/s^2 (the plugin's ramps, set just
  under tyre grip so the wheels neither spin nor lock), wheelbase 0.254 m,
  steering limit 0.786 rad, steering lag ~0.2 s, grip ~10 m/s^2.
Grip is a friction circle: sqrt((k*a_long)^2 + a_lat^2) must stay under it,
with braking weighted k = 1.5 because only the rear wheels brake and they lose
load under braking (a Gazebo car that braked hard into a bend spun). Beyond the
circle the episode ends as a spin.
Each episode randomises these plus sensing noise and delay.

Action (both in [-1, 1]): speed command (-1 = 0 m/s, +1 = V_MAX) and steering
angle command (fraction of the steering limit). Observation: see `_obs`.
Reward: metres of progress along the centreline; crash (leaving the cone
corridor, or exceeding grip) ends the episode with a penalty.
"""
import math
from pathlib import Path

import gymnasium as gym
import numpy as np

from saurcon_plan.track import Track
from saurcon_plan.vehicle import CTRL_DT, STEER_MAX, V_MAX, WHEELBASE  # noqa: F401 (re-exported)
PHYS_DT = 0.01
LOOKAHEAD = np.array([0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15])
OBS_DIM = 7 + 2 * len(LOOKAHEAD)
CRASH_PENALTY = 10.0
BRAKE_WEIGHT = 1.5        # rear-only braking uses grip faster (see module docstring)


def default_worlds():
    here = Path(__file__).resolve()
    for root in [*here.parents]:
        w = root / 'src' / 'middle_earth' / 'worlds'
        if w.is_dir():
            return w
    import os
    return Path(os.environ['SAURCON_WS']) / 'src' / 'middle_earth' / 'worlds'


def load_tracks(worlds=None):
    w = Path(worlds) if worlds else default_worlds()
    return [Track.from_world(w / 'racetrack.world'), Track.from_world(w / 'racetrack.world', reverse=True),
            Track.from_world(w / 'basement.world'), Track.from_world(w / 'basement.world', reverse=True)]


def observe(track, i, x, y, yaw, v, yaw_rate, steer, prev_action):
    """Policy observation from a (possibly estimated) car state."""
    e, dpsi = track.frenet(x, y, yaw, i)
    pts = track.xy[track.ahead(i, LOOKAHEAD)]
    c, s = math.cos(yaw), math.sin(yaw)
    dx, dy = pts[:, 0] - x, pts[:, 1] - y
    bx, by = c * dx + s * dy, -s * dx + c * dy
    head = [v / 10.0, yaw_rate / 5.0, steer / STEER_MAX, prev_action[0], prev_action[1],
            e / max(track.half_width, 1e-3), dpsi]
    return np.concatenate([head, bx / 10.0, by / 10.0]).astype(np.float32)


class RaceEnv(gym.Env):
    metadata = {'render_modes': []}

    def __init__(self, tracks=None, track_weights=(0.55, 0.15, 0.15, 0.15), randomize=True,
                 max_time=45.0, start=None, seed=None):
        self.tracks = tracks or load_tracks()
        self.w = np.array(track_weights[:len(self.tracks)], float); self.w /= self.w.sum()
        self.randomize, self.max_steps, self.start = randomize, int(max_time / CTRL_DT), start
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, (OBS_DIM,), np.float32)
        self.action_space = gym.spaces.Box(-1.0, 1.0, (2,), np.float32)
        self.np_random, _ = gym.utils.seeding.np_random(seed)

    # --- episode -------------------------------------------------------------------------------
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        r = self.np_random
        opts = options or {}
        ti = opts.get('track', r.choice(len(self.tracks), p=self.w))
        self.track = self.tracks[ti]
        if self.randomize:
            self.accel, self.brake = r.uniform(3.4, 3.8), r.uniform(3.6, 4.0)
            self.grip = r.uniform(8.5, 10.5); self.tau_steer = r.uniform(0.1, 0.3)
            self.pos_noise, self.yaw_noise = r.uniform(0.0, 0.05), r.uniform(0.0, 0.015)
            self.delay = int(r.integers(0, 7))          # physics steps (0-60 ms)
        else:
            self.accel, self.brake, self.grip, self.tau_steer = 3.8, 4.0, 9.5, 0.2
            self.pos_noise = self.yaw_noise = 0.0; self.delay = 0
        if self.start is not None or 'start_s' in opts:
            s0 = opts.get('start_s', self.start); e0 = dpsi0 = v0 = 0.0
        else:
            s0 = r.uniform(0, self.track.length); e0 = r.uniform(-0.2, 0.2)
            dpsi0 = r.uniform(-0.1, 0.1); v0 = r.uniform(0, 4)
        i = int(np.searchsorted(self.track.s, s0 % self.track.length)) % len(self.track.s)
        h = self.track.heading[i]
        self.x = self.track.xy[i, 0] - math.sin(h) * e0
        self.y = self.track.xy[i, 1] + math.cos(h) * e0
        self.yaw, self.v, self.steer, self.v_cmd, self.steer_cmd = h + dpsi0, v0, 0.0, v0, 0.0
        self.i, self.progress, self.steps, self.t = i, 0.0, 0, 0.0
        self.prev_action = np.array([v0 / V_MAX * 2 - 1, 0.0], np.float32)
        self.history = [(self.x, self.y, self.yaw, self.v, 0.0, self.steer)] * 8
        self.lap_times, self.last_lap_progress = [], 0.0
        return self._obs(), {}

    def step(self, action):
        a = np.clip(np.asarray(action, np.float32), -1, 1)
        self.v_cmd = (float(a[0]) + 1) / 2 * V_MAX
        self.steer_cmd = float(a[1]) * STEER_MAX
        crashed = False
        for _ in range(int(round(CTRL_DT / PHYS_DT))):
            dv = float(np.clip(self.v_cmd - self.v, -self.brake * PHYS_DT, self.accel * PHYS_DT))
            self.v += dv
            a_long = dv / PHYS_DT * (BRAKE_WEIGHT if dv < 0 else 1.0)
            self.steer += (self.steer_cmd - self.steer) * min(1.0, PHYS_DT / self.tau_steer)
            yaw_rate = self.v * math.tan(self.steer) / WHEELBASE
            if math.hypot(a_long, self.v * yaw_rate) > self.grip:
                crashed = True            # outside the friction circle: the Gazebo car spins out
            self.yaw += yaw_rate * PHYS_DT
            self.x += self.v * math.cos(self.yaw) * PHYS_DT
            self.y += self.v * math.sin(self.yaw) * PHYS_DT
            self.t += PHYS_DT
            self.history.append((self.x, self.y, self.yaw, self.v, yaw_rate, self.steer))
        self.history = self.history[-8:]
        j = self.track.project(self.x, self.y, hint=self.i)
        ds = (self.track.s[j] - self.track.s[self.i] + self.track.length / 2) % self.track.length - self.track.length / 2
        self.i = j; self.progress += ds
        e, _ = self.track.frenet(self.x, self.y, self.yaw, j)
        if abs(e) > self.track.half_width:
            crashed = True
        if self.progress - self.last_lap_progress >= self.track.length:
            self.lap_times.append(self.t); self.last_lap_progress += self.track.length
        reward = ds - 0.02 * float(np.sum((a - self.prev_action) ** 2))
        if crashed:
            reward -= CRASH_PENALTY
        self.prev_action = a; self.steps += 1
        truncated = self.steps >= self.max_steps
        info = {'laps': len(self.lap_times), 'lap_times': list(self.lap_times), 'crashed': crashed,
                'progress': self.progress, 'speed': self.v}
        return self._obs(), float(reward), crashed, truncated, info

    def _obs(self):
        x, y, yaw, v, yr, steer = self.history[-1 - self.delay]
        r = self.np_random
        if self.pos_noise:
            x += r.normal(0, self.pos_noise); y += r.normal(0, self.pos_noise)
            yaw += r.normal(0, self.yaw_noise); v *= 1 + r.normal(0, 0.02)
        i = self.track.project(x, y, hint=self.i)
        return observe(self.track, i, x, y, yaw, v, yr, steer, self.prev_action)
