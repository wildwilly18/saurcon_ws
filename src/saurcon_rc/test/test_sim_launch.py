"""full_sim_saurcon.launch.py: the cone follower switch and the map origin read from the world.

Run:  source /opt/ros/jazzy/setup.bash && source install/setup.bash
      python3 -m pytest -q src/saurcon_rc/test
"""
import importlib.util
from pathlib import Path

import pytest
from launch import LaunchContext

WS = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    'full_sim', Path(__file__).parents[1] / 'launch' / 'full_sim_saurcon.launch.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def ctx(**cfg):
    c = LaunchContext()
    base = dict(cone_follower='false', follower_speed_limit='12.0', cone_debug_csv='',
                world=str(WS / 'src/middle_earth/worlds/racetrack.world'))
    base.update(cfg)
    c.launch_configurations.update(base)
    return c


def test_follower_off_by_default():
    assert m.cone_follower(ctx()) == []


def test_follower_node_and_parameters():
    c = ctx(cone_follower='true', follower_speed_limit='1.5', cone_debug_csv='/tmp/f.csv')
    node = m.cone_follower(c)[0]
    assert node.node_package == 'saurcon_plan' and node.node_executable == 'cone_follower'
    assert m.follower_parameters(c) == {'use_sim_time': True, 'speed_limit': 1.5, 'debug_csv': '/tmp/f.csv'}
    assert 'debug_csv' not in m.follower_parameters(ctx(cone_follower='true'))


def test_map_origin_racetrack():
    assert m.world_map_origin(str(WS / 'src/middle_earth/worlds/racetrack.world')) == '-1.1270 0.0000 0.000000'


def test_map_origin_rotated_spawn():
    x, y, yaw = (float(v) for v in m.world_map_origin(str(WS / 'src/middle_earth/worlds/feature_warehouse.world')).split())
    assert yaw == pytest.approx(1.39022, abs=1e-5)
    assert (x, y) == pytest.approx((12.8022, -0.1249), abs=1e-3)


def test_map_origin_unreadable_world_falls_back():
    assert m.world_map_origin('/nonexistent.world') == m.RTAB_MAP_ORIGIN
