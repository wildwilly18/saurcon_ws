#!/usr/bin/env python3
"""What the cone policy's weave looks like: lateral offset and steering along the lap.

usage: oscillation_plot.py <model.zip> <gazebo-run-dir> <out.png>
Top: lateral offset from the centreline vs distance along the track, Gazebo run (ground
truth from <run>/log.csv) and the same policy in MuJoCo (simulated detector, 2 laps).
Middle: the policy's steering command in MuJoCo, and the steering the car actually reached.
Bottom: spectrum of the offset on the straights (where the line should be straight).
"""
import csv
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src' / 'saurcon_rl'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src' / 'saurcon_plan'))
from saurcon_rl.cone_env import MujocoConeEnv  # noqa: E402
from saurcon_rl.env import STEER_MAX, load_tracks  # noqa: E402
from saurcon_rl.train import race_start_s  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402

REAR = 0.127


def straight(x, y):
    return (-9.5 < x < 6.0) and (abs(y) < 1.2 or abs(y - 4) < 1.2)


def gazebo_trace(run, track):
    rows = list(csv.reader(open(Path(run) / 'log.csv')))[1:]
    g = np.array([[float(r[0]), float(r[2]), float(r[3]), float(r[4])] for r in rows if r[1] == 'gt'])
    mv = np.where(np.hypot(*np.diff(g[:, 1:3], axis=0).T) > 0.005)[0]; g = g[mv[0]:mv[-1]]
    out, i, prog, last = [], None, 0.0, None
    for t, x, y, yaw in g:
        x, y = x - REAR * math.cos(yaw), y - REAR * math.sin(yaw)
        i = track.project(x, y, hint=i); e, _ = track.frenet(x, y, yaw, i)
        if last is not None:
            prog += (track.s[i] - last + track.length / 2) % track.length - track.length / 2
        last = track.s[i]
        out.append((t, prog, e, x, y))
    return np.array(out)


def mujoco_trace(model, laps=2):
    env = MujocoConeEnv(load_tracks(), randomize=False, max_time=120, seed=0)
    obs, _ = env.reset(options={'track': 0, 'start_s': race_start_s(env.tracks[0])})
    out = []
    for _ in range(2400):
        a, _ = model.predict(obs, deterministic=True)
        obs, _, term, trunc, info = env.step(a)
        e, _ = env.track.frenet(env.x, env.y, env.yaw, env.i)
        out.append((env.t, info['progress'], e, env.x, env.y, float(np.clip(a[1], -1, 1)) * STEER_MAX, env.steer))
        if term or trunc or info['laps'] >= laps:
            break
    return np.array(out), env.track


def spectrum(tr):
    """Offset on straight stretches, resampled every 5 cm; returns wavelengths and power."""
    segs, cur = [], []
    for p, e, x, y in tr:
        if straight(x, y):
            cur.append((p, e))
        elif len(cur) > 40:
            segs.append(np.array(cur)); cur = []
        else:
            cur = []
    if len(cur) > 40:
        segs.append(np.array(cur))
    acc, n = None, 0
    for sgm in segs:
        s = np.arange(sgm[0, 0], sgm[-1, 0], 0.05)
        if len(s) < 64:
            continue
        e = np.interp(s, sgm[:, 0], sgm[:, 1]); e = (e - e.mean()) * np.hanning(len(e))
        f = np.fft.rfftfreq(256, 0.05); P = np.abs(np.fft.rfft(e, 256)) ** 2
        acc = P if acc is None else acc + P; n += 1
    return f[1:], acc[1:] / max(n, 1)


def main():
    model_path, run, out = sys.argv[1], sys.argv[2], sys.argv[3]
    model = PPO.load(model_path, device='cpu')
    mj, track = mujoco_trace(model)
    gz = gazebo_trace(run, track)
    INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
    BLUE, ORANGE = '#2a78d6', '#eb6834'
    plt.rcParams.update({'figure.facecolor': SURF, 'axes.facecolor': SURF, 'axes.edgecolor': GRID,
                         'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK,
                         'axes.grid': True, 'grid.color': GRID, 'axes.spines.top': False,
                         'axes.spines.right': False, 'font.size': 10, 'axes.titlesize': 11,
                         'axes.titleweight': 'bold', 'axes.titlelocation': 'left', 'legend.frameon': False})
    fig, ax = plt.subplots(3, 1, figsize=(13, 10), gridspec_kw={'height_ratios': [1.2, 1, 0.9]})
    L = track.length
    for a in ax[:2]:
        for k in range(3):     # shade the bends
            for s0, s1 in ((17.5, 17.5 + math.pi * 2), (35 + math.pi * 2, 35 + 4 * math.pi)):
                a.axvspan(k * L + s0, k * L + s1, color=GRID, alpha=0.5, lw=0)
    ax[0].plot(gz[:, 1], gz[:, 2], color=ORANGE, lw=1.6, label='Gazebo (ROS stack, real detector)')
    ax[0].plot(mj[:, 1], mj[:, 2], color=BLUE, lw=1.6, label='MuJoCo (simulated detector)')
    ax[0].axhline(track.half_width, color=INK2, lw=0.8, ls='--'); ax[0].axhline(-track.half_width, color=INK2, lw=0.8, ls='--')
    ax[0].set_ylabel('lateral offset (m)'); ax[0].set_xlim(0, 2 * L)
    ax[0].set_title('Lateral offset from the centreline along the lap (shaded: bends; dashed: corridor limit)')
    ax[0].legend(loc='upper right', ncol=2)
    ax[1].plot(mj[:, 1], np.degrees(mj[:, 5]), color=BLUE, lw=1.0, alpha=0.55, label='policy steering command')
    ax[1].plot(mj[:, 1], np.degrees(mj[:, 6]), color=BLUE, lw=1.8, label='steering reached')
    ax[1].set_ylabel('steering (deg)'); ax[1].set_xlim(0, 2 * L); ax[1].set_xlabel('distance along the track (m)')
    ax[1].set_title('MuJoCo: steering command vs. steering reached'); ax[1].legend(loc='upper right', ncol=2)
    for tr, c, lab in ((gz[:, 1:], ORANGE, 'Gazebo'), (mj[:, 1:5], BLUE, 'MuJoCo')):
        f, P = spectrum(tr)
        ax[2].plot(1 / f, P / P.max(), color=c, lw=1.8, label=lab)
        k = int(np.argmax(P)); ax[2].annotate(f'{1 / f[k]:.1f} m', (1 / f[k], 1.0), textcoords='offset points',
                                               xytext=(4, -12), color=INK2, fontsize=9)
    ax[2].set_xscale('log'); ax[2].set_xlim(0.4, 13); ax[2].set_xlabel('wavelength (m)')
    ax[2].set_ylabel('relative power'); ax[2].set_xticks([0.5, 1, 1.17, 2, 3, 5, 10])
    ax[2].set_xticklabels(['0.5', '1', 'gate\n1.17', '2', '3', '5', '10'])
    ax[2].set_title('Weave on the straights: spectrum of the lateral offset'); ax[2].legend(loc='upper right')
    fig.tight_layout(); fig.savefig(out, dpi=120)
    for name, tr in (('gazebo', gz), ('mujoco', mj)):
        st = np.array([straight(x, y) for x, y in tr[:, 3:5]])
        print(f'{name}: offset std on straights {tr[st, 2].std():.3f} m, peak-to-peak {np.ptp(tr[st, 2]):.2f} m')
    sc = mj[:, 5]; d = np.diff(sc)
    print(f'mujoco steering command: mean |change| per step {np.degrees(np.abs(d)).mean():.1f} deg, '
          f'saturated {np.mean(np.abs(sc) > 0.95 * STEER_MAX) * 100:.0f}% of steps, '
          f'sign flips {np.count_nonzero(np.diff(np.sign(sc[np.abs(sc) > 0.02])))}/{len(sc)} steps')
    print('saved', out)


if __name__ == '__main__':
    main()
