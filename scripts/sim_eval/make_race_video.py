#!/usr/bin/env python3
"""Compose a race video from a Gazebo run: onboard camera with cone detections | chase camera.

usage: make_race_video.py <run-dir> <output.mp4> [--from-motion]
Needs a run recorded with CHASE=1 (scripts/sim_eval/runsim.sh): <run>/frames (onboard,
from logger.py), <run>/chase (gz_camera_recorder.py) and <run>/log.csv (ground truth).
Detections are recomputed on the onboard frames with the same detector the ROS cone
policy uses (Gazebo colour band, ground-plane ranging; only colour frames are logged).
"""
import csv
import math
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src' / 'saurcon_rl'))
from saurcon_rl.cones import ConeDetector  # noqa: E402

START_X = -1.0            # start line (model-origin x), as in race_driver.py


def main():
    run, out = Path(sys.argv[1]), sys.argv[2]
    rows = list(csv.reader(open(run / 'log.csv')))[1:]
    gt = np.array([[float(r[0]), float(r[2]), float(r[3]), float(r[4])] for r in rows if r[1] == 'gt'])
    frames = [(float(r[0]), int(r[2])) for r in rows if r[1] == 'frame']
    chase = [(float(r['t']), int(r['frame'])) for r in csv.DictReader(open(run / 'chase' / 'stamps.csv'))]
    ct = np.array([c[0] for c in chase])
    moving = np.where(np.hypot(*np.diff(gt[:, 1:3], axis=0).T) > 0.005)[0]
    t0 = gt[moving[0], 0] if len(moving) else gt[0, 0]
    t_end = gt[moving[-1] + 1, 0] + 2.0 if len(moving) else gt[-1, 0]   # stop 2 s after the car last moved
    # start-line crossings (forwards, bottom straight) -> lap times
    cross = [gt[k, 0] for k in range(1, len(gt)) if abs(gt[k, 2]) < 1.5 and gt[k - 1, 1] < START_X <= gt[k, 1]]
    fx = 320 / math.tan(1.204 / 2)
    det = ConeDetector(fx, fx, 320, 200, camera_height=0.137)
    writer = None
    for ts, idx in frames:
        if ts < t0 - 1.0 or ts > t_end or not len(ct):
            continue
        onboard = cv2.imread(str(run / 'frames' / f'{idx:06d}.jpg'))
        j = int(np.argmin(abs(ct - ts)))
        side = cv2.imread(str(run / 'chase' / f'{chase[j][1]:06d}.jpg'))
        if onboard is None or side is None:
            continue
        side = cv2.resize(side, (onboard.shape[1], onboard.shape[0]))
        for d in det.detect(onboard):
            cv2.circle(onboard, (int(d.u), int(d.v)), 7, (255, 200, 0), 2)
            cv2.putText(onboard, f'{d.range:.1f}', (int(d.u) - 10, int(d.v) + 19),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        k = int(np.argmin(abs(gt[:, 0] - ts))); k2 = min(k + 5, len(gt) - 1)
        v = np.hypot(*(gt[k2, 1:3] - gt[k, 1:3])) / max(gt[k2, 0] - gt[k, 0], 1e-3)
        done = [c for c in cross if c <= ts]
        laps = max(len(done) - 1, 0)
        last = f'  last lap {done[-1] - done[-2]:.2f}s' if len(done) > 1 else ''
        frame = np.hstack([onboard, side])
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 28), (0, 0, 0), -1)
        cv2.putText(frame, f'Gazebo  t {ts - t0:6.2f}s   v {v:4.1f} m/s   laps {laps}{last}   '
                           f'onboard OAK-D + cone detections | chase camera',
                    (10, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        if writer is None:
            # play in real (simulated) time: frame rate = logged onboard frames per second of sim time
            sel = [f for f in frames if t0 - 1.0 <= f[0] <= t_end]
            fps = max(1.0, (len(sel) - 1) / max(sel[-1][0] - sel[0][0], 1e-3))
            writer = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*'avc1'), fps, (frame.shape[1], frame.shape[0]))
        writer.write(frame)
    if writer is not None:
        writer.release()
    laps = [round(b - a, 2) for a, b in zip(cross, cross[1:])]
    print(f'video {out}; start-line crossings {len(cross)}, lap times {laps}')


if __name__ == '__main__':
    main()
