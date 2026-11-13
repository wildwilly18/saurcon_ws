"""Stale-input handling of the two driving nodes (review findings 1 and 2).

The nodes are built without ROS communication: a fake clock, TF buffer, policy and publisher
stand in, so nothing is actuated. rclpy is initialised only because the cone node publishes
when rclpy.ok().

Run:  source /opt/ros/jazzy/setup.bash
      PYTHONPATH=src/saurcon_rl:$PYTHONPATH .venv-rl/bin/python -m pytest -q src/saurcon_rl/test
"""
import math
import os
from types import SimpleNamespace

import numpy as np
import pytest

os.environ.setdefault('ROS_DOMAIN_ID', '231')
os.environ.setdefault('ROS_LOCALHOST_ONLY', '1')
rclpy = pytest.importorskip('rclpy')
from tf2_ros import TransformException  # noqa: E402

from saurcon_rl.cone_env import ConeMemory  # noqa: E402
from saurcon_rl.cone_follower import ConeFollower  # noqa: E402
from saurcon_rl.cone_policy_node import ConePolicyNode  # noqa: E402
from saurcon_rl.policy_node import PolicyNode  # noqa: E402


@pytest.fixture(scope='module', autouse=True)
def ros():
    rclpy.init()
    yield
    rclpy.shutdown()


def stamp(t):
    return SimpleNamespace(sec=int(t), nanosec=int(round((t - int(t)) * 1e9)))


class Clock:
    def __init__(self, t=100.0):
        self.t = t


class Pub:
    def __init__(self):
        self.msgs = []

    def publish(self, m):
        self.msgs.append((m.linear.x, m.angular.z))


class FakePolicy:
    """Always full throttle, a little left steering."""
    def predict(self, obs, deterministic=True):
        return np.array([1.0, 0.2], np.float32), None


# --- finding 1: map policy ------------------------------------------------------------------
def state_msg(t, x=0.0, y=0.0, v=3.0):
    return SimpleNamespace(header=SimpleNamespace(stamp=stamp(t)),
                           pose=SimpleNamespace(pose=SimpleNamespace(
                               position=SimpleNamespace(x=x, y=y, z=0.0),
                               orientation=SimpleNamespace(x=0.0, y=0.0, z=0.0, w=1.0))),
                           twist=SimpleNamespace(twist=SimpleNamespace(
                               linear=SimpleNamespace(x=v), angular=SimpleNamespace(z=0.0))))


@pytest.fixture
def map_node(monkeypatch):
    import saurcon_rl.policy_node as pn
    monkeypatch.setattr(pn, 'observe', lambda *a, **k: np.zeros(4, np.float32))
    n = PolicyNode.__new__(PolicyNode)
    clock = Clock()
    n.now_s = lambda: clock.t
    n.warn = lambda text: None
    n.clock, n.pub, n.policy = clock, Pub(), FakePolicy()
    n.track = SimpleNamespace(project=lambda x, y, hint=None: 0)
    n.origin, n.speed_limit, n.state_timeout = (-1.127, 0.0, 0.0), 6.0, 0.25
    n.state, n.state_stamp, n.i = None, None, None
    n.reset_history()
    return n


def test_map_policy_no_motion_before_first_state(map_node):
    for _ in range(5):
        map_node.step()
    assert map_node.pub.msgs and all(m == (0.0, 0.0) for m in map_node.pub.msgs)


def test_map_policy_drives_on_fresh_state(map_node):
    map_node.on_state(state_msg(100.0))
    map_node.step()
    assert map_node.pub.msgs[-1][0] > 0


def test_map_policy_stops_when_state_expires(map_node):
    map_node.on_state(state_msg(100.0))
    map_node.step()
    map_node.clock.t = 100.3                    # past the 0.25 s timeout, no new state
    for _ in range(200):
        map_node.step()
    assert all(m == (0.0, 0.0) for m in map_node.pub.msgs[1:])
    assert map_node.prev_action[0] == -1.0 and map_node.steer_est == 0.0   # history reset


def test_map_policy_old_stamps_do_not_renew(map_node):
    map_node.on_state(state_msg(100.0))
    map_node.clock.t = 100.3
    map_node.on_state(state_msg(100.0))          # same stamp again
    map_node.on_state(state_msg(99.9))           # older
    map_node.step()
    assert map_node.pub.msgs[-1] == (0.0, 0.0)


def test_map_policy_rejects_invalid_state(map_node):
    map_node.on_state(state_msg(100.0, x=float('nan')))
    map_node.step()
    assert map_node.pub.msgs[-1] == (0.0, 0.0)


def test_map_policy_recovers_on_fresh_state(map_node):
    map_node.on_state(state_msg(100.0))
    map_node.clock.t = 101.0
    map_node.step()
    assert map_node.pub.msgs[-1] == (0.0, 0.0)
    map_node.on_state(state_msg(101.0))
    map_node.step()
    assert map_node.pub.msgs[-1][0] > 0


def test_map_policy_origin_applied_once(map_node):
    map_node.on_state(state_msg(100.0, x=0.0))
    assert map_node.state[0] == pytest.approx(-1.127)


# --- finding 2: cone policy -----------------------------------------------------------------
class FakeTF:
    """odom -> base_link at a settable stamp (None: lookup fails)."""
    def __init__(self):
        self.t = None

    def lookup_transform(self, target, source, when):
        if self.t is None:
            raise TransformException('no transform')
        if hasattr(when, 'sec') and abs(when.sec + when.nanosec * 1e-9 - self.t) > 1e-6:
            raise TransformException('no transform at that time')   # only the latest pose is known
        return SimpleNamespace(header=SimpleNamespace(stamp=stamp(self.t)),
                               transform=SimpleNamespace(translation=SimpleNamespace(x=0.0, y=0.0, z=0.0),
                                                         rotation=SimpleNamespace(x=0.0, y=0.0, z=0.0, w=1.0)))


def odom_msg(t, v=3.0):
    return SimpleNamespace(header=SimpleNamespace(stamp=stamp(t)),
                           twist=SimpleNamespace(twist=SimpleNamespace(
                               linear=SimpleNamespace(x=v), angular=SimpleNamespace(z=0.0))))


GATES = np.array([[x, s * 1.1] for x in np.arange(0.5, 6.0, 1.0) for s in (-1, 1)])


def make_cone_node(kind):
    n = ConePolicyNode.__new__(ConePolicyNode)
    clock = Clock()
    n.now_s = lambda: clock.t
    n.warn = lambda text: None
    n.clock, n.pub, n.tf = clock, Pub(), FakeTF()
    n.follower, n.policy, n.debug = (ConeFollower(latency=0.05), None, None) if kind == 'classical' else (None, FakePolicy(), None)
    n.speed_limit, n.image_timeout, n.odom_timeout, n.tf_timeout, n.tf_fallback_max = 6.0, 0.3, 0.25, 0.25, 0.1
    n.tf_wait, n.depth_max_age = 0.25, 0.005
    n.depths, n.pending, n.memory = [], [], ConeMemory()
    n.last_image, n.odom_stamp, n.v, n.yaw_rate = None, None, 0.0, 0.0
    n.stats = dict.fromkeys(['images', 'dets', 'stale_steps', 'rgb', 'depth', 'size_ranged', 'ground_ranged',
                             'tf_fallback', 'tf_dropped', 'tf_lag_ms', 'no_depth'], 0)
    n.reset_history()
    n.detected = []

    def detect(rgb_msg, odom_base):               # stands in for the detector: a fixed set of gates
        t = n.stamp_s(rgb_msg)
        n.detected.append(t)
        n.memory.update(GATES, t)
        n.last_image = t if n.last_image is None else max(n.last_image, t)
    n.detect = detect
    return n


def image(t):
    return SimpleNamespace(header=SimpleNamespace(stamp=stamp(t)))


def all_fresh(n):
    t = n.clock.t
    n.on_odom(odom_msg(t))
    n.tf.t = t
    n.depths = [image(t)]
    n.pending.append(image(t))


@pytest.fixture(params=['classical', 'learned'])
def cone_node(request):
    return make_cone_node(request.param)


def test_cone_policy_drives_with_fresh_inputs(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0


def test_cone_policy_normal_lag_still_drives(cone_node):
    all_fresh(cone_node)
    cone_node.clock.t += 0.1                     # 100 ms lag on every input
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0


def test_cone_policy_stops_on_expired_odometry(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    cone_node.clock.t += 0.3
    cone_node.tf.t = cone_node.clock.t           # TF and images still fresh, odometry messages stopped
    cone_node.depths = [image(cone_node.clock.t)]; cone_node.pending.append(image(cone_node.clock.t))
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_cone_policy_stops_on_expired_tf(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    cone_node.clock.t += 0.3
    cone_node.on_odom(odom_msg(cone_node.clock.t))    # odometry fresh, TF stuck 0.3 s back
    cone_node.depths = [image(cone_node.clock.t)]; cone_node.pending.append(image(cone_node.clock.t))
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)
    assert len(cone_node.memory.xy) == 0         # cone memory cleared with the transform


def test_cone_policy_stops_on_failed_tf_lookup(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    cone_node.tf.t = None
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_cone_policy_reported_case_from_review(cone_node):
    """Fresh image, odometry TF stamped at 1 s, clock at 100 s: used to publish full speed."""
    all_fresh(cone_node)
    cone_node.tf.t = 1.0
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_cone_policy_late_processing_does_not_renew_image(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    old = cone_node.clock.t
    cone_node.clock.t += 0.4                     # an image captured at `old` is only processed now
    cone_node.on_odom(odom_msg(cone_node.clock.t)); cone_node.tf.t = cone_node.clock.t
    cone_node.depths = [image(old)]; cone_node.pending.append(image(old))
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_cone_policy_fallback_pose_must_be_close_to_image(cone_node):
    all_fresh(cone_node)
    cone_node.pending.clear()
    t_img = cone_node.clock.t - 0.3              # waited past tf_wait; its own pose never came
    cone_node.depths = [image(t_img)]; cone_node.pending.append(image(t_img))
    cone_node.process_pending()                  # FakeTF has no history: the exact-stamp lookup
    assert cone_node.stats['tf_dropped'] == 1    # returns the latest (0.3 s off) -> dropped
    assert not cone_node.detected


def test_cone_policy_recovers_after_interruption(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    cone_node.tf.t = None
    for _ in range(10):
        cone_node.clock.t += 0.05
        cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)
    cone_node.clock.t += 0.05
    all_fresh(cone_node)
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0
