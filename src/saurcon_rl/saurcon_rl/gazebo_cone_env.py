"""Cone-vision racing inside Gazebo: train or fine-tune the cone policy on the real sensor chain.

Each environment starts its own headless Gazebo server (racetrack world, its own
GZ_PARTITION) and drives it in lock-step through gz-transport, without ROS:

  step(action):  send /cmd_vel  ->  world control multi_step (50 ms = 5 physics steps)
                 -> wait for the sim clock and for the OAK RGB-D frames rendered in that window
                 -> for each new frame: degrade the depth like oak_depth.py, run
                    cones.ConeDetector, put the cone base points into the cone memory in the
                    odometry frame (pose from the AckermannSteering odometry at the image stamp)
                 -> observation = cone_env.encode(memory in current base_link, v, yaw rate, ...)

That is the same chain cone_policy_node runs in ROS (same detector thresholds, depth
model, camera mount, 20 Hz control, and the plugin's yaw-rate steering interface fed
the measured speed), so what the policy learns here is what it meets on the car in sim.
Ground truth (dynamic_pose/info) is the referee only: progress along the centreline,
the cone-corridor limit and the stall rule, exactly as in MujocoConeEnv.

The world is run with real_time_factor 0 (as fast as it can render): about 37 steps/s
for one server, about 80 steps/s in total for six on one 8 GB GPU (2026-11-12).
Needs the ROS 2 environment sourced (gz Python bindings, ros_gz) and the RL venv.
"""
import atexit
import importlib.util
import math
import os
import re
import signal
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import cv2
import gymnasium as gym
import numpy as np

from .cone_env import (CONE_OBS_DIM, STALL_GRACE_S, STALL_S, STALL_SPEED, ConeMemory, encode,
                       slew_steer, smooth_penalty)
from .cones import ConeDetector
from .env import CRASH_PENALTY, CTRL_DT, STEER_MAX, V_MAX, WHEELBASE
from .track import Track

WS = Path(__file__).resolve().parents[3]
WORLD = WS / 'src/middle_earth/worlds/racetrack.world'
WORLD_NAME = 'warehouse_racetrack'
VEHICLE = 'rc_vehicle'
REAR_AXLE_BACK = 0.127          # m: rear axle (base_link) behind the model origin
CAMERA_X, CAMERA_HEIGHT = 0.219, 0.137   # camera ahead of base_link; above the floor
HFOV, WIDTH, HEIGHT = 1.204, 640, 400
RGB_PERIOD = 1 / 15             # s: OAK RGB-D update rate in the model
PHYS_DT = 0.01
CONE_RE = re.compile(r'<name>(cone_gate_[^<]+)</name>\s*<pose>([^<]+)</pose>')
SPIN_SLIP = math.radians(25)


def _degrade_depth():
    """oak_depth.degrade_depth (the simulated OAK stereo depth), loaded from its script."""
    path = WS / 'src/saurcon_nav/scripts/oak_depth.py'
    spec = importlib.util.spec_from_file_location('oak_depth', path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.degrade_depth


def _die_with_parent():
    """In the Gazebo child: get SIGTERM when the Python worker that started it dies."""
    import ctypes
    ctypes.CDLL('libc.so.6', use_errno=True).prctl(1, signal.SIGTERM)   # PR_SET_PDEATHSIG


def training_world(src=WORLD):
    """The racetrack world with the real-time throttle off (steps as fast as it renders)."""
    text = re.sub(r'<real_time_factor>[^<]*</real_time_factor>', '<real_time_factor>0</real_time_factor>',
                  Path(src).read_text())
    out = Path(tempfile.gettempdir()) / f'saurcon_gz_train_{os.getuid()}' / Path(src).name
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(f'.{os.getpid()}.tmp'); tmp.write_text(text); tmp.replace(out)
    return out


class GazeboConeEnv(gym.Env):
    metadata = {'render_modes': []}

    def __init__(self, tracks=None, randomize=True, max_time=45.0, start=None, seed=None,
                 world=WORLD, partition=None, start_delay=0.0, **_):
        from gz.msgs10.clock_pb2 import Clock
        from gz.msgs10.image_pb2 import Image
        from gz.msgs10.odometry_pb2 import Odometry
        from gz.msgs10.pose_v_pb2 import Pose_V
        from gz.msgs10.twist_pb2 import Twist
        from gz.transport13 import Node
        self.randomize, self.max_steps, self.start = randomize, int(max_time / CTRL_DT), start
        self.np_random, _ = gym.utils.seeding.np_random(seed)
        self.tracks = [Track.from_world(world)]          # referee: centreline, corridor
        self.track = self.tracks[0]
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, (CONE_OBS_DIM,), np.float32)
        self.action_space = gym.spaces.Box(-1.0, 1.0, (2,), np.float32)
        self.cone_poses = [(n, *map(float, p.split())) for n, p in CONE_RE.findall(Path(world).read_text())]
        fx = WIDTH / 2 / math.tan(HFOV / 2)
        self.detector = ConeDetector(fx, fx, WIDTH / 2, HEIGHT / 2, camera_height=CAMERA_HEIGHT)
        self.degrade = _degrade_depth()
        self.depth_rng = np.random.default_rng(seed)

        # --- Gazebo server in its own partition -------------------------------------------------
        self.partition = partition or f'saurcon_train_{os.getpid()}_{id(self) & 0xffff}'
        os.environ['GZ_PARTITION'] = self.partition       # read by gz-transport at Node creation
        env = dict(os.environ)
        env['GZ_SIM_RESOURCE_PATH'] = ':'.join([str(WS / 'src/middle_earth/models'), str(WS / 'src/middle_earth'),
                                                env.get('GZ_SIM_RESOURCE_PATH', '')])
        self.log = open(Path(tempfile.gettempdir()) / f'{self.partition}.log', 'w')
        time.sleep(start_delay)        # stagger servers: loading several at once stalls the GPU
        self.server = subprocess.Popen(['gz', 'sim', '-s', '--headless-rendering', str(training_world(world))],
                                       env=env, stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True,
                                       preexec_fn=_die_with_parent)
        atexit.register(self.close)

        self.Twist, self.Pose_V = Twist, Pose_V
        self.node = Node()
        self.lock = threading.Lock()
        self.clock, self.clock_ev = -1.0, threading.Event()
        self.gt = None                                    # (t, x, y, yaw, roll) of the model origin
        self.odom = []                                    # (t, x, y, yaw, v, yaw_rate)
        self.rgb, self.depth = {}, {}                     # stamp -> image
        stamp = lambda h: round(h.stamp.sec + h.stamp.nsec * 1e-9, 4)
        W = f'/world/{WORLD_NAME}'

        def on_clock(m):
            self.clock = m.sim.sec + m.sim.nsec * 1e-9; self.clock_ev.set()

        def on_pose(m):
            for p in m.pose:
                if p.name == VEHICLE:
                    q = p.orientation
                    yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
                    roll = math.atan2(2 * (q.w * q.x + q.y * q.z), 1 - 2 * (q.x * q.x + q.y * q.y))
                    self.gt = (stamp(m.header), p.position.x, p.position.y, yaw, roll)

        def on_odom(m):
            q = m.pose.orientation
            yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
            with self.lock:
                self.odom.append((stamp(m.header), m.pose.position.x, m.pose.position.y, yaw,
                                  m.twist.linear.x, m.twist.angular.z))
                del self.odom[:-100]

        def on_image(store):
            def f(m):
                with self.lock:
                    store[stamp(m.header)] = m
                    for k in sorted(store)[:-4]:
                        del store[k]
            return f

        subs = [(Clock, W + '/clock', on_clock), (Pose_V, W + '/dynamic_pose/info', on_pose),
                (Odometry, '/model/rc_ackermann_vehicle/odom', on_odom),
                (Image, '/oak_sim/rgb/image', on_image(self.rgb)),
                (Image, '/oak_sim/rgb/depth_image', on_image(self.depth))]
        self.cmd_pub = self.node.advertise('/model/rc_ackermann_vehicle/cmd_vel', Twist)
        self.W = W
        for msg_t, topic, cb in subs:
            self.node.subscribe(msg_t, topic, cb)
        deadline = time.time() + 300
        while self.clock < 0:                              # wait for the server to come up
            if time.time() > deadline or self.server.poll() is not None:
                raise RuntimeError(f'Gazebo server did not start (see {self.log.name})')
            self._control(multi_step=1); time.sleep(1.0)
        self.last_frame = -1.0
        self.img_latency, self.cmd_delay, self.cmd_queue = 0.04, 0, []

    # --- Gazebo plumbing -------------------------------------------------------------------------
    def _control(self, **fields):
        from gz.msgs10.boolean_pb2 import Boolean
        from gz.msgs10.world_control_pb2 import WorldControl
        req = WorldControl(); req.pause = True
        for k, v in fields.items():
            setattr(req, k, v)
        # The reply often arrives late even though the request is executed: do not wait for it,
        # the caller watches the sim clock instead.
        self.node.request(self.W + '/control', req, WorldControl, Boolean, 2)

    def _advance(self, dt, wait_frames=True):
        """Step the paused world by dt and wait for the frames rendered in that window."""
        target = self.clock + dt - 1e-4
        while self.clock < target:
            self.clock_ev.clear()
            self._control(multi_step=int(round(dt / PHYS_DT)))
            deadline = time.time() + 2.0
            while self.clock < target and time.time() < deadline:
                self.clock_ev.wait(0.002); self.clock_ev.clear()
            if self.server.poll() is not None:
                raise RuntimeError(f'Gazebo server exited (see {self.log.name})')
        if not wait_frames:
            return
        due = self.clock - RGB_PERIOD - 0.011             # a frame is rendered every 1/15 s
        deadline = time.time() + 0.5
        while time.time() < deadline:
            with self.lock:
                if self.rgb and max(self.rgb) >= due and max(self.depth, default=-1) >= max(self.rgb):
                    break
            time.sleep(0.001)

    def _teleport(self, car, cones):
        """Move the car (model-origin pose x, y, z, yaw) and put every cone back.

        Like the step request, the reply to set_pose often does not come back while the world
        is paused (the request is applied on the next iteration), so send without waiting,
        step one physics iteration and check the ground truth; repeat until the car is there.
        """
        from gz.msgs10.boolean_pb2 import Boolean
        from gz.msgs10.pose_pb2 import Pose
        x, y, z, yaw = car
        v = self.Pose_V()
        poses = [(VEHICLE, x, y, z, yaw)] + ([(n, cx, cy, cz, cyaw) for n, cx, cy, cz, _r, _p, cyaw in self.cone_poses]
                                              if cones else [])
        for name, px, py, pz, pyaw in poses:
            p = v.pose.add(); p.name = name
            p.position.x, p.position.y, p.position.z = px, py, pz
            p.orientation.w, p.orientation.z = math.cos(pyaw / 2), math.sin(pyaw / 2)
        for _ in range(30):
            self.node.request(self.W + '/set_pose_vector', v, self.Pose_V, Boolean, 2)
            self._advance(PHYS_DT, wait_frames=False)
            self._advance(PHYS_DT, wait_frames=False)
            if self.gt is not None and math.hypot(self.gt[1] - x, self.gt[2] - y) < 0.03:
                return
        raise RuntimeError(f'could not move {VEHICLE} to ({x:.2f}, {y:.2f}) (see {self.log.name})')

    def _send(self, v_cmd, steer_cmd, v_meas):
        tw = self.Twist(); tw.linear.x = v_cmd
        # AckermannSteering turns a yaw rate into a steering angle with the speed it is actually
        # doing; feed it the measured speed, as cone_policy_node does.
        tw.angular.z = max(v_meas, 0.0) * math.tan(steer_cmd) / WHEELBASE
        self.cmd_pub.publish(tw)

    def _base_odom(self, t=None):
        """(x, y, yaw, v, yaw_rate) of base_link in the odometry frame, at time t (default latest)."""
        with self.lock:
            od = list(self.odom)
        if not od:
            return 0.0, 0.0, 0.0, 0.0, 0.0
        o = od[-1] if t is None else min(od, key=lambda r: abs(r[0] - t))
        _, x, y, yaw, v, yr = o
        return x - REAR_AXLE_BACK * math.cos(yaw), y - REAR_AXLE_BACK * math.sin(yaw), yaw, v, yr

    def _perceive(self):
        """Run the detector on every frame that has 'arrived' (older than the image latency)."""
        with self.lock:
            frames = [(s, self.rgb[s], self.depth.get(s)) for s in sorted(self.rgb)
                      if self.last_frame < s <= self.clock - self.img_latency + 1e-6]
        for s, rgb, depth in frames:
            self.last_frame = s
            img = np.frombuffer(rgb.data, np.uint8).reshape(rgb.height, rgb.width, 3)
            bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            depth_m = None
            if depth is not None:
                z = np.frombuffer(depth.data, np.float32).reshape(depth.height, depth.width)
                depth_m = self.degrade(z, cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), self.depth_rng).astype(np.float32) / 1000.0
            dets = self.detector.detect(bgr, depth_m)
            # optical frame (x right, y down, z forward) -> base_link
            base = np.array([(CAMERA_X + d.p_cam[2], -d.p_cam[0]) for d in dets]).reshape(-1, 2)
            x, y, yaw, _, _ = self._base_odom(s)
            c, si = math.cos(yaw), math.sin(yaw)
            # timestamped at processing time, as cone_policy_node does
            self.memory.update(np.column_stack([x + c * base[:, 0] - si * base[:, 1],
                                                y + si * base[:, 0] + c * base[:, 1]]), self.clock)
            self.n_dets += len(dets)

    def _referee_pose(self):
        t, x, y, yaw, roll = self.gt
        return x - REAR_AXLE_BACK * math.cos(yaw), y - REAR_AXLE_BACK * math.sin(yaw), yaw, roll

    # --- gym API ---------------------------------------------------------------------------------
    def reset(self, seed=None, options=None):
        if seed is not None:
            self.np_random, _ = gym.utils.seeding.np_random(seed)
        r, opts = self.np_random, options or {}
        # stop the car (the plugin ramps the speed down), then teleport it and put the cones back
        for _ in range(40):
            self._send(0.0, 0.0, 0.0); self._advance(CTRL_DT)
            if abs(self._base_odom()[3]) < 0.05:
                break
        if self.start is not None or 'start_s' in opts:
            s0, e0, dpsi0 = opts.get('start_s', self.start), 0.0, 0.0
        else:
            s0, e0, dpsi0 = r.uniform(0, self.track.length), r.uniform(-0.2, 0.2), r.uniform(-0.1, 0.1)
        i = int(np.searchsorted(self.track.s, s0 % self.track.length)) % len(self.track.s)
        h = self.track.heading[i]
        bx = self.track.xy[i, 0] - math.sin(h) * e0
        by = self.track.xy[i, 1] + math.cos(h) * e0
        yaw = h + dpsi0
        self._teleport((bx + REAR_AXLE_BACK * math.cos(yaw), by + REAR_AXLE_BACK * math.sin(yaw), 0.05, yaw), cones=True)
        for _ in range(10):                                # settle on the wheels (0.5 s)
            self._send(0.0, 0.0, 0.0); self._advance(CTRL_DT)
        self.memory, self.n_dets = ConeMemory(), 0
        # Latency: lock-step stepping has none, the ROS stack has some (bridge, depth sync,
        # node timers). Randomised in training so the policy holds up with either.
        if self.randomize:
            self.img_latency, self.cmd_delay = float(r.uniform(0.0, 0.1)), int(r.integers(0, 2))
        else:
            self.img_latency, self.cmd_delay = 0.04, 0
        self.cmd_queue = []
        with self.lock:
            self.last_frame = max(self.rgb, default=self.last_frame)
        x, y, _, _ = self._referee_pose()
        self.i = self.track.project(x, y)
        self.progress, self.steps, self.t, self.slow_steps = 0.0, 0, 0.0, 0
        self.lap_times, self.last_lap_progress = [], 0.0
        self.prev_action = np.array([-1.0, 0.0], np.float32)
        self.steer_est = 0.0
        self.prev_ref = self._referee_pose()
        self._perceive()
        return self._obs(), {}

    def _obs(self):
        x, y, yaw, v, yr = self._base_odom()
        rel, ages = self.memory.relative(x, y, yaw, self.clock)
        self.v = v
        return encode(rel, v, yr, self.steer_est, self.prev_action, ages)

    def step(self, action):
        a = np.clip(np.asarray(action, np.float32), -1, 1).copy()
        prev_steer = float(self.prev_action[1])
        a[1] = slew_steer(prev_steer, float(a[1]), CTRL_DT)
        v_cmd = (float(a[0]) + 1) / 2 * V_MAX
        steer_cmd = float(a[1]) * STEER_MAX
        self.cmd_queue.append((v_cmd, steer_cmd))
        v_out, steer_out = self.cmd_queue.pop(0) if len(self.cmd_queue) > self.cmd_delay else (0.0, 0.0)
        self._send(v_out, steer_out, self.v)
        self.steer_est += (steer_cmd - self.steer_est) * min(1.0, CTRL_DT / 0.2)
        self._advance(CTRL_DT)
        self.t += CTRL_DT
        self._perceive()
        x, y, yaw, roll = self._referee_pose()
        px, py, _, _ = self.prev_ref; self.prev_ref = (x, y, yaw, roll)
        vx, vy = (x - px) / CTRL_DT, (y - py) / CTRL_DT
        v_long = math.cos(yaw) * vx + math.sin(yaw) * vy
        v_lat = -math.sin(yaw) * vx + math.cos(yaw) * vy
        crashed = abs(roll) > 0.6 or (abs(v_long) > 1.0 and abs(math.atan2(v_lat, abs(v_long))) > SPIN_SLIP)
        j = self.track.project(x, y, hint=self.i)
        L = self.track.length
        ds = (self.track.s[j] - self.track.s[self.i] + L / 2) % L - L / 2
        self.i = j; self.progress += ds
        e, _ = self.track.frenet(x, y, yaw, j)
        crashed |= abs(e) > self.track.half_width
        if self.progress - self.last_lap_progress >= L:
            self.lap_times.append(self.t); self.last_lap_progress += L
        _, _, _, _, yr = self._base_odom()
        reward = (ds - 0.02 * float(np.sum((a - self.prev_action) ** 2)) - (CRASH_PENALTY if crashed else 0.0)
                  - smooth_penalty(float(a[1]), prev_steer, yr, v_long, float(self.track.curvature[j])))
        self.prev_action = a; self.steps += 1
        info = {'laps': len(self.lap_times), 'lap_times': list(self.lap_times), 'crashed': crashed,
                'progress': self.progress, 'speed': v_long}
        self.slow_steps = self.slow_steps + 1 if abs(v_long) < STALL_SPEED else 0
        if not crashed and self.t > STALL_GRACE_S and self.slow_steps * CTRL_DT >= STALL_S:
            crashed = True; reward -= CRASH_PENALTY; info['stalled'] = True
        return self._obs(), float(reward), crashed, self.steps >= self.max_steps, info

    def close(self):
        if getattr(self, 'server', None) is not None and self.server.poll() is None:
            try:
                os.killpg(self.server.pid, signal.SIGTERM); self.server.wait(10)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(self.server.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self.server = None
