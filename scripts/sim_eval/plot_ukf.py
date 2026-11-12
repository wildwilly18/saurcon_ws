#!/usr/bin/env python3
"""Plot the wheel/gyro UKF (/saurcon/nav_state) of one run against ground truth.

usage: plot_ukf.py <run-dir> <output-dir>
Needs a log.csv whose 'nav' rows carry variances (logger.py from 2026-11-12 on).
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK, INK2, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e4e3df'
BLUE, BAND, ORANGE, AQUA = '#2a78d6', '#cde2fb', '#eb6834', '#1baf7a'
plt.rcParams.update({'figure.facecolor': SURF, 'axes.facecolor': SURF, 'axes.edgecolor': GRID,
    'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'text.color': INK,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.spines.top': False,
    'axes.spines.right': False, 'font.size': 10, 'axes.titlesize': 11, 'axes.titleweight': 'bold',
    'legend.frameon': False})

run, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
rows = {'gt': [], 'nav': [], 'map': [], 'odomukf': [], 'rtab': []}
for r in csv.reader(open(run / 'log.csv')):
    if r[1] in rows:
        rows[r[1]].append([float(v) for v in [r[0]] + r[2:] if v != ''])
gt = np.array(rows['gt']); nav = np.array(rows['nav']); mp = np.array(rows['map']) if rows['map'] else None
# Fused runs (two UKFs): 'nav' is the map-frame UKF fusing RTAB-Map, 'odomukf' the
# odometry-only UKF and 'rtab' RTAB-Map's own pose (newest optimized node).
fused = bool(rows['odomukf'])
odo = np.array(rows['odomukf']) if fused else None
rt = np.array(rows['rtab']) if rows['rtab'] else None
if fused: mp = None   # map -> base_link TF is then the fused UKF itself
gt = gt[np.argsort(gt[:, 0])]; nav = nav[np.argsort(nav[:, 0])]
if nav.shape[1] < 8: sys.exit('nav rows have no variances; re-run with the current logger.py')

def wrap(a): return np.arctan2(np.sin(a), np.cos(a))
def truth_at(t):
    yaw = np.unwrap(gt[:, 3])
    return np.interp(t, gt[:, 0], gt[:, 1]), np.interp(t, gt[:, 0], gt[:, 2]), np.interp(t, gt[:, 0], yaw)

# Truth speed from positions; the car starts moving where it first exceeds 0.15 m/s.
dt = np.diff(gt[:, 0]); keep = dt > 1e-6
sp_t = gt[1:, 0][keep]; sp = (np.hypot(np.diff(gt[:, 1]), np.diff(gt[:, 2]))[keep] / dt[keep])
sp = np.convolve(sp, np.ones(9) / 9, 'same')
t_move = sp_t[np.argmax(sp > 0.15)]

# Both the UKF (odom frame) and RTAB-Map (map frame) start at the start pose:
# express them in world coordinates with one SE(2) transform from the first UKF sample.
t0 = nav[0, 0]; X0, Y0, H0 = truth_at(t0); c, s = math.cos(H0), math.sin(H0)
def to_world(a):
    a = a.copy(); x, y = a[:, 1].copy(), a[:, 2].copy()
    a[:, 1] = X0 + c * x - s * y; a[:, 2] = Y0 + s * x + c * y; a[:, 3] = a[:, 3] + H0
    return a
nav = to_world(nav); mp = to_world(mp) if mp is not None else None
odo = to_world(odo[np.argsort(odo[:, 0])]) if odo is not None else None
rt = to_world(rt[np.argsort(rt[:, 0])]) if rt is not None else None
NAME = 'UKF fused with RTAB-Map' if fused else 'UKF (wheel speed + gyro)'

# Score only the driving window: until the truth stops after the laps.
moving = sp > 0.15
t_stop = sp_t[np.where(moving)[0][-1]] if moving.any() else gt[-1, 0]
w = (nav[:, 0] >= t_move - 2) & (nav[:, 0] <= t_stop + 2); n = nav[w]
t = n[:, 0] - t_move
tx, ty, th = truth_at(n[:, 0])
ex, ey, eh = n[:, 1] - tx, n[:, 2] - ty, np.degrees(wrap(n[:, 3] - th))
sx, sy, sh = np.sqrt(n[:, 5]), np.sqrt(n[:, 6]), np.degrees(np.sqrt(n[:, 7]))
pos = np.hypot(ex, ey)
inside = lambda e, sd: float(np.mean(np.abs(e) <= 3 * sd))
metrics = {
    'duration_s': round(float(t[-1] - t[0]), 1),
    'position_rms_m': round(float(np.sqrt(np.mean(pos ** 2))), 3),
    'position_max_m': round(float(pos.max()), 3),
    'position_end_m': round(float(pos[-1]), 3),
    'heading_rms_deg': round(float(np.sqrt(np.mean(eh ** 2))), 2),
    'heading_max_deg': round(float(np.abs(eh).max()), 2),
    'final_sigma_x_m': round(float(sx[-1]), 3), 'final_sigma_y_m': round(float(sy[-1]), 3),
    'final_sigma_heading_deg': round(float(sh[-1]), 3),
    'fraction_within_3sigma': {'x': round(inside(ex, sx), 3), 'y': round(inside(ey, sy), 3),
                               'heading': round(inside(eh, sh), 3)},
}
def score(a):
    a = a[(a[:, 0] >= t_move - 2) & (a[:, 0] <= t_stop + 2)]
    x, y, h = truth_at(a[:, 0]); e = np.hypot(a[:, 1] - x, a[:, 2] - y)
    return a, e, {'position_rms_m': round(float(np.sqrt(np.mean(e ** 2))), 3),
                  'position_max_m': round(float(e.max()), 3),
                  'heading_rms_deg': round(float(np.sqrt(np.mean(np.degrees(wrap(a[:, 3] - h)) ** 2))), 2)}
if odo is not None: odo, odo_e, metrics['odometry_ukf'] = score(odo)
if rt is not None: rt, rt_e, metrics['rtabmap_pose'] = score(rt)
if mp is not None:
    m = mp[(mp[:, 0] >= t_move - 2) & (mp[:, 0] <= t_stop + 2)]
    mx, my, _ = truth_at(m[:, 0]); mpos = np.hypot(m[:, 1] - mx, m[:, 2] - my)
    metrics['rtabmap_position_rms_m'] = round(float(np.sqrt(np.mean(mpos ** 2))), 3)
json.dump(metrics, open(out / 'ukf_metrics.json', 'w'), indent=1)
print(json.dumps(metrics, indent=1))
title_run = run.name if run.name != 'run' else run.parent.name

# ---- Figure 1: top-down trajectory ----
fig, ax = plt.subplots(figsize=(11, 4.6))
g = gt[(gt[:, 0] >= t_move - 2) & (gt[:, 0] <= t_stop + 2)]
ax.plot(g[:, 1], g[:, 2], color=INK2, lw=3, label='Ground truth', zorder=2)
if mp is not None: ax.plot(m[:, 1], m[:, 2], color=ORANGE, lw=1.5, label='RTAB-Map (map → base_link)', zorder=3)
if odo is not None: ax.plot(odo[:, 1], odo[:, 2], color=AQUA, lw=1.5, label='Odometry-only UKF', zorder=3)
if rt is not None: ax.plot(rt[:, 1], rt[:, 2], color=ORANGE, lw=0, marker='o', ms=3, label='RTAB-Map pose (filter input)', zorder=3)
ax.plot(n[:, 1], n[:, 2], color=BLUE, lw=1.5, label=NAME, zorder=4)
ax.set_aspect('equal'); ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)')
ax.legend(loc='upper center', ncol=4 if fused else 3, bbox_to_anchor=(0.5, 1.13))
ax.set_title(f'Top-down path, {metrics["duration_s"]:.0f} s of driving — {NAME}: position error RMS '
             f'{metrics["position_rms_m"]:.3f} m, max {metrics["position_max_m"]:.3f} m', loc='left', pad=30)
fig.tight_layout(); fig.savefig(out / 'ukf_trajectory.png', dpi=130); plt.close(fig)

# ---- Figure 2: states vs truth ----
fig, axs = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
tt = g[:, 0] - t_move; gh = np.degrees(np.unwrap(g[:, 3]))
nh = np.degrees(np.radians(np.interp(n[:, 0], g[:, 0], gh)) + np.radians(eh))
for ax, gv, nv, lab in ((axs[0], g[:, 1], n[:, 1], 'x (m)'), (axs[1], g[:, 2], n[:, 2], 'y (m)'),
                         (axs[2], gh, nh, 'heading (deg, unwrapped)')):
    ax.plot(tt, gv, color=INK2, lw=3, label='Ground truth'); ax.plot(t, nv, color=BLUE, lw=1.5, label=NAME)
    ax.set_ylabel(lab)
st = (sp_t >= t_move - 2) & (sp_t <= t_stop + 2)
axs[3].plot(sp_t[st] - t_move, sp[st], color=INK2, lw=3); axs[3].plot(t, n[:, 4], color=BLUE, lw=1.5)
axs[3].set_ylabel('speed (m/s)'); axs[3].set_xlabel('time since the car starts moving (s)')
axs[0].legend(loc='upper right', ncol=2)
axs[0].set_title(f'{NAME}: state estimates vs. ground truth', loc='left')
fig.tight_layout(); fig.savefig(out / 'ukf_states.png', dpi=130); plt.close(fig)

# ---- Figure 3: errors with the filter's own 3-sigma bounds ----
fig, axs = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
for ax, e, sd, lab, key in ((axs[0], ex, sx, 'x error (m)', 'x'), (axs[1], ey, sy, 'y error (m)', 'y'),
                            (axs[2], eh, sh, 'heading error (deg)', 'heading')):
    ax.fill_between(t, -3 * sd, 3 * sd, color=BAND, lw=0, label='UKF ±3σ (its own covariance)')
    ax.plot(t, e, color=BLUE, lw=1.5, label=f'{NAME} error')
    ax.axhline(0, color=INK2, lw=0.8); ax.set_ylabel(lab)
    ax.text(0.995, 0.92, f'{100 * metrics["fraction_within_3sigma"][key]:.0f}% of samples inside ±3σ',
            transform=ax.transAxes, ha='right', va='top', color=INK2, fontsize=9)
if odo is not None: axs[3].plot(odo[:, 0] - t_move, odo_e, color=AQUA, lw=1.5, label='Odometry-only UKF')
if rt is not None: axs[3].plot(rt[:, 0] - t_move, rt_e, color=ORANGE, lw=0, marker='o', ms=2.5, label='RTAB-Map pose')
axs[3].plot(t, pos, color=BLUE, lw=1.5, label=NAME); axs[3].set_ylabel('position error (m)')
if fused: axs[3].legend(loc='upper left', ncol=3)
axs[3].set_xlabel('time since the car starts moving (s)')
axs[0].legend(loc='upper left', ncol=2)
axs[0].set_title(f'{NAME}: error against ground truth, with the filter\'s own uncertainty', loc='left')
fig.tight_layout(); fig.savefig(out / 'ukf_errors.png', dpi=130); plt.close(fig)
print('plots in', out)
