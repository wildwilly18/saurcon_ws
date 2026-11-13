"""Map-policy pose source and origin per localization mode (review finding 4).

Run:  source /opt/ros/jazzy/setup.bash && source install/setup.bash
      python3 -m pytest -q src/saurcon_rc/test
"""
import importlib.util
from pathlib import Path

import pytest
from launch import LaunchContext

spec = importlib.util.spec_from_file_location(
    'full_sim', Path(__file__).parents[1] / 'launch' / 'full_sim_saurcon.launch.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def ctx(**cfg):
    c = LaunchContext()
    base = dict(use_aruco='false', slam='false', fuse_slam='true', visual_odometry='false',
                policy_map_origin='', policy_model='/tmp/model.zip', policy_speed_limit='6',
                world='/tmp/racetrack.world')
    base.update(cfg)
    c.launch_configurations.update(base)
    return c


def test_aruco_uses_world_origin():
    assert m.policy_map_origin(ctx(use_aruco='true')) == '0 0 0'


def test_aruco_rejects_a_map_origin():
    with pytest.raises(ValueError):
        m.policy_map_origin(ctx(use_aruco='true', policy_map_origin='-1.127 0 0'))


def test_rtab_default_origin_is_spawn():
    assert m.policy_map_origin(ctx(slam='true')) == '-1.127 0 0'


def test_rtab_origin_configurable():
    assert m.policy_map_origin(ctx(slam='true', policy_map_origin='2 3 1.57')) == '2 3 1.57'
    with pytest.raises(ValueError):
        m.policy_map_origin(ctx(slam='true', policy_map_origin='2 3'))


@pytest.mark.parametrize('cfg', [
    dict(slam='true', fuse_slam='false'),            # nav_state is odometry
    dict(slam='true', visual_odometry='true'),       # nav_state is visual odometry
    dict(),                                          # no localization at all
])
def test_odometry_only_modes_rejected(cfg):
    with pytest.raises(ValueError):
        m.policy_map_origin(ctx(**cfg))


def test_origin_reaches_the_node(tmp_path, monkeypatch):
    monkeypatch.setattr(m.os.path, 'exists', lambda p: True)       # pretend the RL venv exists
    for cfg, want in ((dict(use_aruco='true'), 'map_origin:=[0.0, 0.0, 0.0]'),
                      (dict(slam='true'), 'map_origin:=[-1.127, 0.0, 0.0]')):
        proc = m.policy(ctx(**cfg), str(tmp_path))[0]
        cmd = ' '.join(''.join(p.perform(ctx(**cfg)) if hasattr(p, 'perform') else str(p) for p in part)
                       for part in proc.cmd)
        assert want in cmd
