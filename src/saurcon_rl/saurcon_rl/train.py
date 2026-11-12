#!/usr/bin/env python3
"""Train a racing policy with PPO in the fast environment.

usage: python -m saurcon_rl.train --out rl_runs/ppo1 [--steps 20000000] [--envs 12] [--env bicycle|mujoco]

Every --eval-every steps it drives the racetrack from the race start with no
randomisation and logs the standing-start and flying lap times. The policy
with the best flying lap (two clean laps required) is saved as best_model.zip.
"""
import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import SubprocVecEnv, VecMonitor

from saurcon_rl.env import RaceEnv, load_tracks

ENVS = {'bicycle': RaceEnv}


def env_class(name):
    if name == 'mujoco':
        from saurcon_rl.mujoco_env import MujocoRaceEnv
        return MujocoRaceEnv
    if name == 'mujoco_cones':
        from saurcon_rl.cone_env import MujocoConeEnv
        return MujocoConeEnv
    return ENVS[name]

RACE_START_WORLD = (-1.127, 0.0)   # rear axle at the Gazebo spawn pose


def race_start_s(track):
    return float(track.s[track.project(*RACE_START_WORLD)])


def evaluate(model, env, laps=2):
    obs, _ = env.reset(options={'track': 0, 'start_s': race_start_s(env.tracks[0])})
    info, top = {}, 0.0
    for _ in range(int(laps * 200 / 0.05)):
        action, _ = model.predict(obs, deterministic=True)
        obs, _, term, trunc, info = env.step(action)
        top = max(top, info['speed'])
        if term or trunc or info['laps'] >= laps:
            break
    t = info.get('lap_times', [])
    return {'laps': len(t), 'crashed': bool(info.get('crashed')),
            'standing_lap_s': round(t[0], 3) if t else None,
            'flying_lap_s': round(t[1] - t[0], 3) if len(t) > 1 else None,
            'top_speed': round(top, 2), 'progress_m': round(info.get('progress', 0.0), 1)}


class LapEval(BaseCallback):
    def __init__(self, out, every, env_name='bicycle'):
        super().__init__()
        self.out, self.every, self.best, self.next = out, every, math.inf, every
        self.env = env_class(env_name)(load_tracks(), randomize=False, max_time=200)
        self.log = open(out / 'eval.jsonl', 'a')

    def _on_step(self):
        if self.num_timesteps < self.next:
            return True
        self.next += self.every
        r = evaluate(self.model, self.env)
        r['steps'] = self.num_timesteps; r['wall_s'] = round(time.time() - self.t0, 1)
        self.log.write(json.dumps(r) + '\n'); self.log.flush()
        for k in ('standing_lap_s', 'flying_lap_s', 'top_speed', 'progress_m'):
            if r[k] is not None:
                self.logger.record(f'race/{k}', r[k])
        if r['flying_lap_s'] and not r['crashed'] and r['flying_lap_s'] < self.best:
            self.best = r['flying_lap_s']; self.model.save(self.out / 'best_model')
        print(f"[{r['steps']:>9}] laps {r['laps']} crashed {r['crashed']} standing {r['standing_lap_s']} "
              f"flying {r['flying_lap_s']} top {r['top_speed']} m/s  best {self.best}", flush=True)
        return True

    def _on_training_start(self):
        self.t0 = time.time()
        self.next = self.num_timesteps + self.every   # resumed runs continue the step count


def make_env(rank, seed, env_name='bicycle'):
    def f():
        torch.set_num_threads(1)
        return env_class(env_name)(seed=seed + rank)
    return f


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--steps', type=int, default=20_000_000)
    p.add_argument('--envs', type=int, default=12)
    p.add_argument('--eval-every', type=int, default=250_000)
    p.add_argument('--seed', type=int, default=1)
    p.add_argument('--resume', type=Path)
    p.add_argument('--env', choices=['bicycle', 'mujoco', 'mujoco_cones'], default='bicycle')
    p.add_argument('--reset-std', type=float,
                   help='when resuming, reset the action noise std (a converged policy barely explores a new simulator)')
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    venv = VecMonitor(SubprocVecEnv([make_env(i, a.seed * 1000, a.env) for i in range(a.envs)]))
    if a.resume:
        model = PPO.load(a.resume, env=venv, tensorboard_log=str(a.out / 'tb'), device='cpu')
        if a.reset_std:
            with torch.no_grad():
                model.policy.log_std.fill_(math.log(a.reset_std))
    else:
        model = PPO('MlpPolicy', venv, n_steps=1024, batch_size=4096, n_epochs=10, gamma=0.99,
                    gae_lambda=0.95, learning_rate=3e-4, clip_range=0.2, ent_coef=0.0,
                    policy_kwargs=dict(net_arch=[256, 256], log_std_init=-0.5),
                    tensorboard_log=str(a.out / 'tb'), seed=a.seed, verbose=0)
    (a.out / 'config.json').write_text(json.dumps(vars(a), default=str, indent=1))
    model.learn(a.steps, callback=LapEval(a.out, a.eval_every, a.env), progress_bar=False,
                reset_num_timesteps=not a.resume)
    model.save(a.out / 'final_model')
    print('final eval:', evaluate(model, env_class(a.env)(load_tracks(), randomize=False, max_time=200)))


if __name__ == '__main__':
    main()
