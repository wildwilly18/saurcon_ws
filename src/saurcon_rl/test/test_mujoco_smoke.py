"""Smoke tests for the simulation environments, and the classical follower driving in MuJoCo.

Needs the .venv-rl environment (gymnasium, mujoco, stable-baselines3):
  PYTHONPATH=src/saurcon_plan:src/saurcon_rl:$PYTHONPATH MUJOCO_GL=egl \
      .venv-rl/bin/python -m pytest -q src/saurcon_rl/test
"""
import os

import numpy as np
import pytest

os.environ.setdefault('MUJOCO_GL', 'egl')
pytest.importorskip('mujoco')
gym_checker = pytest.importorskip('gymnasium.utils.env_checker')

from saurcon_plan.cone_follower import ConeFollower  # noqa: E402
from saurcon_rl.cone_env import MujocoConeEnv  # noqa: E402
from saurcon_rl.env import RaceEnv, load_tracks  # noqa: E402
from saurcon_rl.mujoco_env import MujocoRaceEnv  # noqa: E402
from saurcon_rl.train import race_start_s  # noqa: E402


@pytest.mark.parametrize('cls', [RaceEnv, MujocoRaceEnv, MujocoConeEnv])
def test_env_api_and_finite_steps(cls):
    env = cls(load_tracks(), seed=0)
    gym_checker.check_env(env, skip_render_check=True)
    obs, _ = env.reset(seed=1)
    for _ in range(40):
        obs, r, term, trunc, _ = env.step(env.action_space.sample())
        assert np.all(np.isfinite(obs)) and np.isfinite(r)
        if term or trunc:
            obs, _ = env.reset()


def test_classical_follower_drives_mujoco():
    """The follower on the simulated detector: 10 s from the race start without crashing."""
    env = MujocoConeEnv(load_tracks(), randomize=False, seed=0)
    env.reset(options={'track': 0, 'start_s': race_start_s(env.tracks[0])})
    f = ConeFollower()
    env.memory.horizon = f.memory_s
    progress = 0.0
    for _ in range(200):
        rel, _ = env.memory.relative(env.x, env.y, env.yaw, env.t)
        _, _, term, trunc, info = env.step(f.action(rel, env.v, env.state[4]))
        progress = info['progress']
        assert not term, 'crashed'
        if trunc:
            break
    assert progress > 20.0                     # metres along the track in 10 s
