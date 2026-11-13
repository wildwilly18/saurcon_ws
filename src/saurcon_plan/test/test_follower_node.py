"""Stale-input handling of the cone follower node (branch review finding 2).

The node is built without ROS communication: a fake clock, TF buffer and publisher stand in,
so nothing is actuated. rclpy is initialised only because the node publishes when rclpy.ok().

Run:  source /opt/ros/jazzy/setup.bash
      PYTHONPATH=src/saurcon_plan:$PYTHONPATH python3 -m pytest -q src/saurcon_plan/test
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

from saurcon_plan.cone_follower import ConeFollower  # noqa: E402
from saurcon_plan.cone_follower_node import ConeFollowerNode  # noqa: E402
from saurcon_plan.memory import ConeMemory  # noqa: E402


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


# --- finding 2: cone follower node -----------------------------------------------------------------
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


def make_cone_node():
    n = ConeFollowerNode.__new__(ConeFollowerNode)
    clock = Clock()
    n.now_s = lambda: clock.t
    n.warn = lambda text: None
    n.clock, n.pub, n.tf = clock, Pub(), FakeTF()
    n.follower, n.debug = ConeFollower(latency=0.05), None
    n.speed_limit, n.image_timeout, n.odom_timeout, n.tf_timeout, n.tf_fallback_max = 6.0, 0.3, 0.25, 0.25, 0.1
    n.tf_wait, n.depth_max_age = 0.25, 0.005
    n.memory_s = n.follower.memory_s
    n.depths, n.pending, n.memory = [], [], ConeMemory(horizon=n.memory_s)
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


@pytest.fixture
def cone_node():
    return make_cone_node()


def test_follower_node_drives_with_fresh_inputs(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0


def test_follower_node_normal_lag_still_drives(cone_node):
    all_fresh(cone_node)
    cone_node.clock.t += 0.1                     # 100 ms lag on every input
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0


def test_follower_node_stops_on_expired_odometry(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    cone_node.clock.t += 0.3
    cone_node.tf.t = cone_node.clock.t           # TF and images still fresh, odometry messages stopped
    cone_node.depths = [image(cone_node.clock.t)]; cone_node.pending.append(image(cone_node.clock.t))
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_follower_node_stops_on_expired_tf(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    cone_node.clock.t += 0.3
    cone_node.on_odom(odom_msg(cone_node.clock.t))    # odometry fresh, TF stuck 0.3 s back
    cone_node.depths = [image(cone_node.clock.t)]; cone_node.pending.append(image(cone_node.clock.t))
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)
    assert len(cone_node.memory.xy) == 0         # cone memory cleared with the transform


def test_follower_node_stops_on_failed_tf_lookup(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    cone_node.tf.t = None
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_follower_node_reported_case_from_review(cone_node):
    """Fresh image, odometry TF stamped at 1 s, clock at 100 s: used to publish full speed."""
    all_fresh(cone_node)
    cone_node.tf.t = 1.0
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_follower_node_late_processing_does_not_renew_image(cone_node):
    all_fresh(cone_node)
    cone_node.step()
    old = cone_node.clock.t
    cone_node.clock.t += 0.4                     # an image captured at `old` is only processed now
    cone_node.on_odom(odom_msg(cone_node.clock.t)); cone_node.tf.t = cone_node.clock.t
    cone_node.depths = [image(old)]; cone_node.pending.append(image(old))
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)


def test_follower_node_fallback_pose_must_be_close_to_image(cone_node):
    all_fresh(cone_node)
    cone_node.pending.clear()
    t_img = cone_node.clock.t - 0.3              # waited past tf_wait; its own pose never came
    cone_node.depths = [image(t_img)]; cone_node.pending.append(image(t_img))
    cone_node.process_pending()                  # FakeTF has no history: the exact-stamp lookup
    assert cone_node.stats['tf_dropped'] == 1    # returns the latest (0.3 s off) -> dropped
    assert not cone_node.detected


def test_follower_node_recovers_after_interruption(cone_node):
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


def test_follower_node_recovers_after_clock_reset(cone_node):
    """A simulation reset sends the clock back: stop, forget cones from the old run, recover on fresh data."""
    all_fresh(cone_node)
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0              # driving at t = 100 s
    cone_node.clock.t = 5.0                            # clock jumps backwards
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)        # stamps from the "future" are not fresh
    assert len(cone_node.memory.xy) == 0               # cones of the old run are forgotten
    all_fresh(cone_node)                               # fresh data on the new clock
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0               # recovered
