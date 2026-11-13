"""MuJoCo raceway environment with the same interface as env.RaceEnv.

Same observation, action, reward, termination and episode setup as the fast
bicycle environment, so policies move between the two (and Gazebo) unchanged.
The difference is the car: a rigid-body MuJoCo model with tyre contacts, so
weight transfer, wheel spin, lock-up and spin-outs come from the physics instead
of a friction-circle rule.

The drive mimics Gazebo's AckermannSteering plugin: the commanded speed is
ramped at the acceleration/braking limits, rear wheels get velocity targets with
the plugin's differential, and the front knuckles get Ackermann angles.
A spin (sideslip over 25 deg at speed, or a roll-over) ends the episode.
"""
import math

import mujoco
import numpy as np

from .env import CRASH_PENALTY, CTRL_DT, LOOKAHEAD, OBS_DIM, STEER_MAX, V_MAX, RaceEnv, observe
from .mujoco_model import REAR_AXLE_X, TRACK, WHEEL_R, WHEELBASE, ackermann, build_mjcf

SPIN_SLIP = math.radians(25)


class MujocoRaceEnv(RaceEnv):
    def __init__(self, *args, cone_mode=None, timestep=0.002, **kwargs):
        super().__init__(*args, **kwargs)
        self.cone_mode = cone_mode
        self.models = {}
        self.timestep = timestep
        self.substeps = int(round(CTRL_DT / timestep))

    # --- model per track (cones differ); without cones one model serves all tracks ----------
    def _model(self, track):
        key = track.name if self.cone_mode else None
        if key not in self.models:
            xml = build_mjcf(cones=track.cones if self.cone_mode else None,
                             cone_mode=self.cone_mode or 'visual', timestep=self.timestep)
            m = mujoco.MjModel.from_xml_string(xml)
            self.models[key] = (m, mujoco.MjData(m), m.geom_friction.copy(), m.body_mass.copy())
        return self.models[key]

    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)   # picks track, start, limits, noise
        self.m, self.d, fric0, mass0 = self._model(self.track)
        r = self.np_random
        self.m.geom_friction[:] = fric0 * (r.uniform(0.85, 1.05) if self.randomize else 1.0)
        self.m.body_mass[:] = mass0 * (r.uniform(0.9, 1.1) if self.randomize else 1.0)
        mujoco.mj_resetData(self.m, self.d)
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        bx, by = self.x - REAR_AXLE_X * c, self.y - REAR_AXLE_X * s   # chassis origin from rear axle
        self.d.qpos[:7] = [bx, by, 0.006, math.cos(self.yaw / 2), 0, 0, math.sin(self.yaw / 2)]
        self.d.qvel[:3] = [self.v * c, self.v * s, 0]
        for name in ('left_rear_spin', 'right_rear_spin', 'left_front_spin', 'right_front_spin'):
            self.d.qvel[self.m.joint(name).dofadr[0]] = self.v / WHEEL_R
        mujoco.mj_forward(self.m, self.d)
        self.v_target = self.v
        self._read_state()
        self.history = [self.state] * 8
        return self._obs(), info

    def _read_state(self):
        d, m = self.d, self.m
        q = d.qpos[3:7]
        yaw = math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2))
        roll = math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] ** 2 + q[2] ** 2))
        site = d.site('base_link').xpos
        vel = np.zeros(6)
        mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_SITE, m.site('base_link').id, vel, 0)
        c, s = math.cos(yaw), math.sin(yaw)
        v_long, v_lat = c * vel[3] + s * vel[4], -s * vel[3] + c * vel[4]
        steer = 0.5 * (d.qpos[m.joint('left_steer').qposadr[0]] + d.qpos[m.joint('right_steer').qposadr[0]])
        self.x, self.y, self.yaw, self.v = float(site[0]), float(site[1]), yaw, v_long
        self.v_lat, self.roll, self.steer = v_lat, roll, float(steer)
        self.state = (self.x, self.y, yaw, v_long, float(vel[2]), self.steer)

    def step(self, action):
        a = np.clip(np.asarray(action, np.float32), -1, 1)
        self.v_cmd = (float(a[0]) + 1) / 2 * V_MAX
        delta = float(a[1]) * STEER_MAX
        left, right = ackermann(delta)
        kappa = math.tan(np.clip(delta, -1.2, 1.2)) / WHEELBASE
        crashed = False
        for _ in range(self.substeps):
            dv = float(np.clip(self.v_cmd - self.v_target, -self.brake * self.timestep, self.accel * self.timestep))
            self.v_target += dv
            w = self.v_target / WHEEL_R
            self.d.ctrl[:] = [w * (1 - kappa * TRACK / 2), w * (1 + kappa * TRACK / 2), left, right]
            mujoco.mj_step(self.m, self.d)
        self.t += CTRL_DT
        self._read_state()
        self.history.append(self.state); self.history = self.history[-8:]
        if (abs(self.v) > 1.0 and abs(math.atan2(self.v_lat, abs(self.v))) > SPIN_SLIP) or abs(self.roll) > 0.6:
            crashed = True
        j = self.track.project(self.x, self.y, hint=self.i)
        ds = (self.track.s[j] - self.track.s[self.i] + self.track.length / 2) % self.track.length - self.track.length / 2
        self.i = j; self.progress += ds
        e, _ = self.track.frenet(self.x, self.y, self.yaw, j)
        if abs(e) > self.track.half_width:
            crashed = True
        if self.progress - self.last_lap_progress >= self.track.length:
            self.lap_times.append(self.t); self.last_lap_progress += self.track.length
        reward = ds - 0.02 * float(np.sum((a - self.prev_action) ** 2)) - (CRASH_PENALTY if crashed else 0.0)
        self.prev_action = a; self.steps += 1
        info = {'laps': len(self.lap_times), 'lap_times': list(self.lap_times), 'crashed': crashed,
                'progress': self.progress, 'speed': self.v, 'slip_deg': math.degrees(math.atan2(self.v_lat, max(abs(self.v), 1e-3)))}
        return self._obs(), float(reward), crashed, self.steps >= self.max_steps, info
