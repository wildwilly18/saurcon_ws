"""Compare identification drives (e.g. Gazebo vs MuJoCo): python -m saurcon_rl.sysid_compare a.csv b.csv"""
import csv
import math
import sys

import numpy as np

WHEELBASE = 0.254


def analyse(path):
    d = np.array([[float(x) for x in r] for r in list(csv.reader(open(path)))[1:]])
    u = np.unique(d[:, 0], return_index=True)[1]
    t, cv, cs, x, y, yaw = d[u].T
    dt = np.diff(t); tm = t[1:]; k = np.ones(5) / 5
    vx, vy = np.diff(x) / dt, np.diff(y) / dt
    sp = np.convolve(np.hypot(vx, vy), k, 'same'); yr = np.convolve(np.diff(np.unwrap(yaw)) / dt, k, 'same')
    slip = np.degrees(np.arctan2(np.sin(np.arctan2(vy, vx) - yaw[1:]), np.cos(np.arctan2(vy, vx) - yaw[1:])))
    cvm, csm = cv[1:], cs[1:]
    m = (cvm == 15) & (sp > 0.5) & (sp < 14); accel = np.polyfit(tm[m], sp[m], 1)[0]
    j = np.where(cvm == 15)[0][-1] + 1
    mb = (cvm == 0) & (tm > tm[j]) & (tm < tm[j] + 4) & (sp > 1); brake = np.polyfit(tm[mb], sp[mb], 1)[0]
    grid = {}
    for v in (2, 3, 4, 5, 6, 8):
        for s in (0.15, 0.3, 0.5, 0.786):
            q = np.where((cvm == v) & (csm == s))[0]; q = q[len(q) // 2:]
            grid[(v, s)] = (np.median(sp[q]), np.median(np.abs(yr[q])), np.median(sp[q]) * np.median(np.abs(yr[q])),
                            np.median(np.abs(slip[q])))
    return accel, brake, grid


def main():
    res = [analyse(p) for p in sys.argv[1:3]]
    print(f'{"":14s}' + ''.join(f'{p.split("/")[-2]:>34s}' for p in sys.argv[1:3]))
    print(f'{"accel m/s2":14s}' + ''.join(f'{r[0]:34.2f}' for r in res))
    print(f'{"brake m/s2":14s}' + ''.join(f'{r[1]:34.2f}' for r in res))
    print(f'{"v_cmd steer":14s}' + '      v_act yaw  a_lat slip' * 2)
    for key in res[0][2]:
        print(f'{key[0]:5.0f} {key[1]:6.3f}  ' + ''.join('     %5.2f %4.2f %5.2f %4.0f' % r[2][key] for r in res))


if __name__ == '__main__':
    main()
