#!/usr/bin/env python3
"""Compute every numerical reference result quoted in the solutions manual.

Run from the workspace root:
  PYTHONPATH=src/saurcon_plan:src/saurcon_rl:$PYTHONPATH MUJOCO_GL=egl \
      .venv-rl/bin/python docs/course/solutions/reference_results.py [--skip-mujoco]
"""
import math
import sys
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(WS / 'src' / 'saurcon_plan'))
sys.path.insert(0, str(WS / 'src' / 'saurcon_rl'))


def p1_1():
    L, Tw = 0.254, 0.165
    for rho in (1.0, 2.0, 5.0):
        di, do = math.atan(L / (rho - Tw / 2)), math.atan(L / (rho + Tw / 2))
        print(f'1.1  rho={rho} m: inner {math.degrees(di):.2f} deg, outer {math.degrees(do):.2f} deg')


def p1_4():
    from saurcon_plan.track import Track
    tr = Track.from_world(WS / 'src/middle_earth/worlds/racetrack.world')
    s, kap = tr.s, np.abs(tr.curvature)
    ds = np.diff(np.append(s, tr.length)); n = len(s)

    def lap(k, mg=10.0, a=3.8, b=4.0, vmax=12.0, coupled=True):
        v2 = np.minimum(mg / np.maximum(kap, 1e-6), vmax ** 2)
        for _ in range(2):
            for i in range(n):
                j = (i + 1) % n; ay = v2[i] * kap[i]
                acc = min(a, math.sqrt(max(mg ** 2 - ay ** 2, 0))) if coupled else a
                v2[j] = min(v2[j], v2[i] + 2 * acc * ds[i])
        for _ in range(2):
            for i in range(n - 1, -1, -1):
                j = (i + 1) % n; ay = v2[j] * kap[j]
                br = min(b, math.sqrt(max(mg ** 2 - ay ** 2, 0)) / k) if coupled else b
                v2[i] = min(v2[i], v2[j] + 2 * br * ds[i])
        v = np.sqrt(v2)
        return float(np.sum(ds / np.maximum(v, 1e-3))), v
    T0, _ = lap(1, coupled=False); T1, v1 = lap(1.0); T15, v15 = lap(1.5)
    i = int(np.argmax(v1 - v15))
    print(f'1.4  separate bounds {T0:.3f} s; ellipse k=1 {T1:.3f} s; k=1.5 {T15:.3f} s; '
          f'largest speed loss {(v1 - v15).max():.3f} m/s at s={s[i]:.1f} m')


def p2_2():
    f = 465.7
    for Z in (1, 3, 5):
        w = f * 0.122 / Z
        print(f'2.2  marker 0.122 m at {Z} m: {w:.1f} px wide; 0.3 px corner noise = {Z * 0.3 / f * 1000:.1f} mm laterally')


def p3_2():
    def ctrv(x, dt=0.5, w=2.0):
        px, py, psi, v = x
        return np.array([px + v / w * (math.sin(psi + w * dt) - math.sin(psi)),
                         py + v / w * (math.cos(psi) - math.cos(psi + w * dt)), psi + w * dt, v])
    mu = np.array([0, 0, 0, 3.0])
    for spsi in (0.3, 1.5):
        P = np.diag([0.05 ** 2, 0.05 ** 2, spsi ** 2, 0.5 ** 2])
        row = []
        for a in (0.001, 0.01, 0.1, 0.5, 1.0):
            n, beta, kappa = 4, 2.0, 0.0; lam = a * a * (n + kappa) - n
            Lc = np.linalg.cholesky((n + lam) * P)
            X = [mu] + [mu + Lc[:, i] for i in range(n)] + [mu - Lc[:, i] for i in range(n)]
            Wm = np.full(9, 1 / (2 * (n + lam))); Wm[0] = lam / (n + lam); Wc = Wm.copy(); Wc[0] += 1 - a * a + beta
            Y = np.array([ctrv(x) for x in X]); m = Wm @ Y
            C = sum(Wc[i] * np.outer(Y[i] - m, Y[i] - m) for i in range(9))
            row.append(f'a={a}: W0c={Wc[0]:.3g}, min eig {np.linalg.eigvalsh(C).min():.2e}')
        print(f'3.2  sigma_psi={spsi}, dt=0.5 s, 2 rad/s: ' + '; '.join(row))


def p6_1():
    r = np.array([0.1, 0.2, -10.0]); V = np.array([1.0, 1.1, 0.5, 0.0]); g, lam = 0.99, 0.95
    d = r + g * V[1:] - V[:-1]
    A = np.zeros(3); last = 0.0
    for t in reversed(range(3)):
        last = d[t] + g * lam * last; A[t] = last
    print(f'6.1  deltas {np.round(d, 4)}, GAE advantages {np.round(A, 3)}')


def p9_1():
    f, h, hc = 465.7, 0.137, 0.071
    for Z in (2, 4, 6):
        print(f'9.1  Z={Z} m: ground {100 * Z * Z / (f * h):.1f} cm/px, size {100 * Z * Z / (f * hc):.1f} cm/px')


def p9_5():
    w = 2.2
    for s in (0.65, 1.17):
        inwin = [f'chord k={k} ({k * s:.2f} m)' for k in range(1, 6) if 1.95 <= k * s <= 2.75]
        print(f'9.5  s={s} m: same-side chords in [1.95, 2.75] m: {inwin}')


def p9_7():
    from saurcon_plan.cone_follower import ConeFollower
    from saurcon_rl.cone_env import MujocoConeEnv
    from saurcon_rl.env import load_tracks
    from saurcon_rl.train import race_start_s
    for alat in (5, 7, 10):
        res = []
        for seed in (0, 1, 2):
            env = MujocoConeEnv(load_tracks(), randomize=False, seed=seed, max_time=60)
            env.reset(options={'track': 0, 'start_s': race_start_s(env.tracks[0])})
            fol = ConeFollower(a_lat=alat); env.memory.horizon = fol.memory_s
            maxe = 0.0
            while True:
                rel, _ = env.memory.relative(env.x, env.y, env.yaw, env.t)
                _, _, term, trunc, info = env.step(fol.action(rel, env.v, env.state[4]))
                e, _ = env.track.frenet(env.x, env.y, env.yaw, env.i); maxe = max(maxe, abs(e))
                if term or trunc or info['laps'] >= 2:
                    break
            lt = np.diff([0.0] + list(env.lap_times))
            res.append(f'{"crash" if term else "ok"} laps {np.round(lt, 2).tolist()} max|e| {maxe:.2f}')
        print(f'9.7  a_lat={alat}: ' + ' | '.join(res))


if __name__ == '__main__':
    p1_1(); p1_4(); p2_2(); p3_2(); p6_1(); p9_1(); p9_5()
    if '--skip-mujoco' not in sys.argv:
        p9_7()
