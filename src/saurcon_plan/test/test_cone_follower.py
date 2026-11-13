"""ConeFollower path helpers (review finding 5: along() at distance zero wrapped to the path end)."""
import math

import numpy as np
import pytest

from saurcon_plan.cone_follower import ConeFollower

L_PATH = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])


@pytest.mark.parametrize('dist, expected', [
    (0.0, (0.0, 0.0)),      # was [3, 3]: index -1 picked the last segment
    (-0.5, (0.0, 0.0)),     # before the start: clamp to the first point
    (0.25, (0.25, 0.0)),
    (1.0, (1.0, 0.0)),      # exact vertex
    (1.5, (1.0, 0.5)),
    (2.0, (1.0, 1.0)),      # end point
    (2.5, (1.0, 1.5)),      # extrapolated along the last segment
])
def test_along(dist, expected):
    assert ConeFollower.along(L_PATH, dist) == pytest.approx(expected)


def test_along_skips_repeated_points():
    p = np.array([[0.0, 0.0], [0.0, 0.0], [1.0, 0.0], [1.0, 0.0], [1.0, 1.0], [1.0, 1.0]])
    assert ConeFollower.along(p, 0.0) == pytest.approx((0.0, 0.0))
    assert ConeFollower.along(p, 1.0) == pytest.approx((1.0, 0.0))
    assert ConeFollower.along(p, 1.5) == pytest.approx((1.0, 0.5))
    assert ConeFollower.along(p, 3.0) == pytest.approx((1.0, 2.0))   # last real direction, not 0/0


def test_along_single_point():
    assert ConeFollower.along(np.array([[2.0, 1.0]]), 0.5) == pytest.approx((2.5, 1.0))


def bend(straight, radius, angle, n=30):
    t = np.linspace(0.0, angle, n)[1:]
    arc = np.column_stack([straight + radius * np.sin(t), radius * (1 - np.cos(t))])
    return np.vstack([[0.0, 0.0], [straight, 0.0], arc])


def test_curvature_of_short_bend():
    """0.3 m straight then 1 rad at 0.6 m radius: the case the speed planner sees entering a bend."""
    k, _, length = ConeFollower.max_curvature(bend(0.3, 0.6, 1.0))
    assert length == pytest.approx(0.9, abs=0.01)
    assert k > 1.0                              # was 0.013 /m; a straight reads 0


def test_curvature_of_long_bend_matches_radius():
    k, at, _ = ConeFollower.max_curvature(bend(1.0, 0.6, 2.5))
    assert k == pytest.approx(1 / 0.6, rel=0.05)
    assert at > 1.0                             # found inside the arc, not at the start


def test_curvature_of_straight_is_zero():
    assert ConeFollower.max_curvature(np.array([[0.0, 0.0], [1.0, 0.0], [3.0, 0.0]]))[0] == pytest.approx(0.0)


def test_bend_ahead_limits_speed():
    """Gates curving left at 2.5 m radius: the commanded speed respects the corner, not just v_max."""
    f = ConeFollower()
    r_c, half = 2.5, 1.1
    t = np.linspace(0.0, 1.6, 9)
    centre = np.column_stack([r_c * np.sin(t), r_c * (1 - np.cos(t))])
    normal = np.column_stack([-np.sin(t), np.cos(t)])
    cones = np.vstack([centre + half * normal, centre - half * normal])
    v_cmd, _ = f.act(cones, v=4.0)
    v_corner = math.sqrt(f.a_lat * r_c)
    k, d_k, _ = f.max_curvature(f.path)
    assert k > 0.25
    assert v_cmd <= math.sqrt(v_corner ** 2 + 2 * f.a_brake * d_k) + 0.3


# Feature warehouse, run fw_loc_v5_repeat, t = 51.6 s: entering a left bend, only the outer
# (right) boundary visible ahead. Gates there are 0.65 m apart along the track, so two cones
# three apart on one side are ~2.07 m apart, inside the gate-width window. The old crossing
# test (against the direction to the midpoint) accepted that chord beside the car, and the
# follower steered at the boundary and left the track.
BEND_ENTRY = np.array([
    [-1.75, 1.11], [-5.43, 1.15], [-3.0, 1.88], [-3.39, -0.89], [-4.91, 0.61], [-1.9, -1.23],
    [-2.64, -1.16], [-4.33, 0.11], [1.47, -0.37], [-3.68, -0.34], [-2.54, 1.56], [-0.15, -1.19],
    [-1.12, -1.24], [-2.94, -0.71], [-2.15, 1.35], [0.69, -0.84], [1.8, -0.5], [-2.16, -0.93],
    [-1.37, -1.02], [2.09, 0.25], [-0.51, -0.94], [1.12, -0.25], [0.37, -0.67], [2.82, 0.95],
    [1.76, 0.3], [3.23, 1.69], [2.29, 0.91], [3.06, 2.23], [2.68, 1.55]])


def test_boundary_chord_is_not_a_gate():
    f = ConeFollower(latency=0.05)
    v, steer = f.act(BEND_ENTRY, v=2.2, yaw_rate=0.54)
    pts = f.path[1:]
    assert len(pts)
    clearance = np.hypot(*(pts[:, None, :] - BEND_ENTRY[None, :, :]).transpose(2, 0, 1)).min()
    assert clearance > 0.5                       # the path keeps off the cones (was 0.0: on a cone)
    assert steer > 0.0                           # turns left, into the bend (was steering right)


def test_midpoint_on_a_cone_is_rejected():
    """Gate cones plus one same-side pair 2.1 m apart beside the car: no midpoint on the boundary."""
    left = [(x, 1.1) for x in np.arange(-1.0, 5.0, 0.65)]
    right = [(x, -1.1) for x in np.arange(-1.0, 5.0, 0.65)]
    cones = np.array(left + right)
    f = ConeFollower()
    f.act(cones, v=2.0)
    assert np.all(np.abs(f.path[1:, 1]) < 0.3)   # stays on the centreline y = 0
