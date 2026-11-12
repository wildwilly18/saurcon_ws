#!/usr/bin/env python3
"""Measure the Gazebo car's dynamics on an empty floor (no ROS needed).

Starts a headless Gazebo with config/sysid.world in its own partition, sends
speed / yaw-rate commands straight to the Ackermann plugin, and records the
true pose. Writes <out>/sysid.csv and prints fitted limits:
  accel / brake rate, steering lag, and the lateral-acceleration (grip) limit.

usage: python3 -m saurcon_rl.sysid <output-dir>            (Gazebo)
       python3 -m saurcon_rl.sysid --mujoco <output-dir>   (MuJoCo model)
"""
import csv
import math
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

try:                                   # Gazebo bindings (need ROS sourced); MuJoCo mode works without
    from gz.transport13 import Node
    from gz.msgs10.pose_v_pb2 import Pose_V
    from gz.msgs10.twist_pb2 import Twist
except ImportError:
    Node = Pose_V = Twist = None

WHEELBASE = 0.254
WORLD = 'warehouse_racetrack'
CMD = '/model/rc_ackermann_vehicle/cmd_vel'


class Recorder:
    def __init__(self):
        self.rows, self.cmd = [], (0.0, 0.0)
        self.node = Node()
        self.pub = self.node.advertise(CMD, Twist)
        if not self.node.subscribe(Pose_V, f'/world/{WORLD}/dynamic_pose/info', self.pose):
            raise RuntimeError('cannot subscribe to poses')

    def pose(self, msg):
        for p in msg.pose:
            if p.name != 'rc_vehicle':
                continue
            q = p.orientation
            yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
            t = msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9
            self.rows.append((t, self.cmd[0], self.cmd[1], p.position.x, p.position.y, yaw))

    def hold(self, v, steer, seconds):
        """Command speed v (m/s) and front steering angle steer (rad) for `seconds` of sim time."""
        omega = v * math.tan(steer) / WHEELBASE   # the plugin takes yaw rate, not angle
        self.cmd = (v, steer)
        msg = Twist(); msg.linear.x = v; msg.angular.z = omega
        t0 = self.rows[-1][0] if self.rows else 0.0
        while not self.rows or self.rows[-1][0] - t0 < seconds:
            self.pub.publish(msg)
            time.sleep(0.02)


def schedule(hold):
    """The identification manoeuvres, shared by Gazebo and MuJoCo."""
    hold(0, 0, 2)
    hold(15, 0, 4); hold(0, 0, 3)                                  # acceleration, braking
    hold(3, 0, 2); hold(3, 0.3, 2); hold(3, -0.3, 2); hold(0, 0, 2) # steering step
    for v in (2, 3, 4, 5, 6, 8):                                   # cornering grid
        for steer in (0.15, 0.3, 0.5, 0.786):
            hold(v, 0, 1.5 + v / 5); hold(v, steer, 2.5)
        hold(0, 0, 3)


def mujoco_main(out):
    """Same drive in the MuJoCo model (python -m saurcon_rl.sysid --mujoco <out>)."""
    import mujoco
    from .mujoco_model import TRACK, WHEEL_R, ackermann, build_mjcf
    m = mujoco.MjModel.from_xml_string(build_mjcf()); d = mujoco.MjData(m)
    st = {'v': 0.0, 't': 0.0}; rows = []
    accel, brake = 3.8, 4.0                       # the Gazebo plugin's ramps
    def hold(v, steer, seconds):
        left, right = ackermann(steer)
        kappa = math.tan(steer) / WHEELBASE
        t_end = st['t'] + seconds
        while st['t'] < t_end:
            st['v'] += float(np.clip(v - st['v'], -brake * m.opt.timestep, accel * m.opt.timestep))
            w = st['v'] / WHEEL_R
            d.ctrl[:] = [w * (1 - kappa * TRACK / 2), w * (1 + kappa * TRACK / 2), left, right]
            mujoco.mj_step(m, d); st['t'] += m.opt.timestep
            if int(round(st['t'] / m.opt.timestep)) % 10 == 0:          # log at 50 Hz like Gazebo
                q = d.qpos[3:7]; p = d.site('base_link').xpos
                yaw = math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2))
                rows.append((st['t'], v, steer, p[0], p[1], yaw))
    schedule(hold)
    return rows


def main():
    if sys.argv[1] == '--mujoco':
        out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
        rows = mujoco_main(out)
        with open(out / 'sysid.csv', 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['t', 'cmd_v', 'cmd_steer', 'x', 'y', 'yaw']); w.writerows(rows)
        print(f'{len(rows)} samples -> {out / "sysid.csv"}')
        return
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    pkg = Path(__file__).resolve().parents[1]
    world = pkg / 'config' / 'sysid.world'
    if not world.exists():   # installed layout
        from ament_index_python.packages import get_package_share_directory
        world = Path(get_package_share_directory('saurcon_rl')) / 'config' / 'sysid.world'
    env = dict(os.environ, GZ_PARTITION=f'sysid_{os.getpid()}')
    me = Path(os.environ.get('SAURCON_WS', Path.cwd())) / 'src' / 'middle_earth'
    env['GZ_SIM_RESOURCE_PATH'] = f'{me / "models"}:{me}'
    os.environ['GZ_PARTITION'] = env['GZ_PARTITION']
    sim = subprocess.Popen(['gz', 'sim', '-s', '-r', str(world)], env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        time.sleep(6)
        r = Recorder()
        schedule(r.hold)
        rows = r.rows
    finally:
        os.killpg(sim.pid, signal.SIGINT); time.sleep(3)
        try: os.killpg(sim.pid, signal.SIGKILL)
        except ProcessLookupError: pass
    with open(out / 'sysid.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t', 'cmd_v', 'cmd_steer', 'x', 'y', 'yaw']); w.writerows(rows)
    print(f'{len(rows)} samples -> {out / "sysid.csv"}')


if __name__ == '__main__':
    main()
