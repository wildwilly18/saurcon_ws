#!/usr/bin/env python3
"""Compose a race video from a Gazebo run: onboard camera with cone detections | chase camera.

usage: make_race_video.py <run-dir> <output.mp4> [--map-from <slam-run-dir>]
Needs <run>/frames (onboard, from logger.py) and <run>/log.csv (ground truth). The chase
camera panel is added if the run was recorded with CHASE=1 (scripts/sim_eval/runsim.sh;
<run>/chase from gz_camera_recorder.py); without it the video is the onboard view only.
If the run had RTAB-Map (slam:=true; capture_map.py saves <run>/maps), a map panel is added
below: the occupancy grid as it was built, the cone map placed with RTAB-Map's pose
(cone_mapping:=rtab), the true cones for reference, and the car's path in the map frame.
If the classical follower logged its state (<run>/follower.csv, launch cone_debug_csv:=...), its
waypoints (the planned centreline) and lookahead target are drawn on the panel too; without SLAM
the panel is then a top-down track view placed with ground truth. --map-from <slam-run-dir> puts
that run's final occupancy grid behind it (same track; the map frame starts at the spawn pose in
both, so the ground-truth pose lines up with it).
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
REAR_AXLE_BACK = 0.127    # base_link (rear axle) behind the model origin
MAP_ORIGIN = (-1.127, 0.0)                   # world position of the map frame (start pose, yaw 0)
CROP = (-14.0, 12.8, -2.4, 6.6)              # map-frame window shown (x0, x1, y0, y1), m
PANEL_W = 1280


def map_records(run):
    """Rows of <run>/maps/index.csv whose grid image exists ([] without SLAM or before any map)."""
    path = run / 'maps' / 'index.csv'
    if not path.exists():
        return []
    try:
        rows = list(csv.DictReader(open(path)))
    except (csv.Error, OSError):
        return []
    ok = []
    for r in rows:
        try:
            float(r['stamp']); float(r['resolution']); float(r['origin_x']); float(r['origin_y'])
            if (run / 'maps' / f"{int(r['frame']):04d}.png").exists():
                ok.append(r)
        except (KeyError, TypeError, ValueError):
            continue
    return ok


class MapPanel:
    """Occupancy grid + cone map + path, in the map frame, for one video frame time."""
    def __init__(self, run, true_world, records=None, background=None):
        self.run = run
        self.maps = [(float(r['stamp']), r) for r in (map_records(run) if records is None else records)]
        self.slam = bool(self.maps)
        self.background = False
        if not self.slam and background is not None:
            bg = map_records(Path(background))
            if bg:                       # that run's final grid, shown from the start
                self.maps = [(-math.inf, dict(bg[-1], _dir=str(background)))]
                self.background = True
        self.cones = []
        if (run / 'cones_rtab.csv').exists():
            for line in open(run / 'cones_rtab.csv'):
                if not line.strip():
                    continue
                t, *pts = line.strip().split(';')
                self.cones.append((float(t), np.array([[float(v) for v in p.split()] for p in pts if p]).reshape(-1, 2)))
        self.closures = []
        if (run / 'closures.json').exists():
            import json
            self.closures = [c['stamp'] for c in json.load(open(run / 'closures.json'))]
        rows = list(csv.reader(open(run / 'log.csv')))[1:]
        self.path = np.array([[float(r[0]), float(r[2]), float(r[3]), float(r[4])]
                              for r in rows if len(r) > 4 and r[1] == 'map'], float).reshape(-1, 4)
        if not self.slam:
            # no map frame: place the car with ground truth (model origin -> rear axle -> map frame)
            gt = np.array([[float(r[0]), float(r[2]), float(r[3]), float(r[4])]
                           for r in rows if len(r) > 4 and r[1] == 'gt'], float).reshape(-1, 4)
            gt[:, 1] -= REAR_AXLE_BACK * np.cos(gt[:, 3]) + MAP_ORIGIN[0]
            gt[:, 2] -= REAR_AXLE_BACK * np.sin(gt[:, 3]) + MAP_ORIGIN[1]
            self.path = gt
        self.waypoints = load_waypoints(run / 'follower.csv', self.path)
        self.true = np.asarray(true_world, float).reshape(-1, 2) - np.array(MAP_ORIGIN)
        x0, x1, y0, y1 = CROP
        self.s = PANEL_W / (x1 - x0)
        self.h = int(round((y1 - y0) * self.s))
        self.cache = (None, None)

    def px(self, x, y):
        x0, x1, y0, y1 = CROP
        return int((x - x0) * self.s), int((y1 - y) * self.s)

    def grid(self, t):
        prior = [m for m in self.maps if m[0] <= t]
        if not prior:
            return np.full((self.h, PANEL_W, 3), 118, np.uint8)
        t_m, r = prior[-1]
        if self.cache[0] == r['frame']:
            return self.cache[1].copy()
        g = cv2.imread(str(Path(r.get('_dir', self.run)) / 'maps' / f"{int(r['frame']):04d}.png"), cv2.IMREAD_GRAYSCALE)
        if g is None:
            return np.full((self.h, PANEL_W, 3), 118, np.uint8)
        res, ox, oy, H = float(r['resolution']), float(r['origin_x']), float(r['origin_y']), g.shape[0]
        x0, x1, y0, y1 = CROP
        a = res * self.s
        M = np.float32([[a, 0, (ox + 0.5 * res - x0) * self.s], [0, a, (y1 - oy - (H - 0.5) * res) * self.s]])
        warped = cv2.warpAffine(g, M, (PANEL_W, self.h), flags=cv2.INTER_NEAREST, borderValue=127)
        img = np.empty((self.h, PANEL_W, 3), np.uint8)
        img[:] = (118, 118, 118)                                # unknown
        img[warped > 200] = (236, 234, 230)                     # free
        img[warped < 60] = (20, 20, 20)                         # occupied
        self.cache = (r['frame'], img)
        return img.copy()

    def render(self, t):
        img = self.grid(t)
        for x, y in self.true:
            cv2.circle(img, self.px(x, y), 5, (60, 160, 60), 1, cv2.LINE_AA)
        mapped = [c for c in self.cones if c[0] <= t]
        n = 0
        if mapped:
            for x, y in mapped[-1][1]:
                cv2.circle(img, self.px(x, y), 4, (0, 120, 255), -1, cv2.LINE_AA)
            n = len(mapped[-1][1])
        trail = self.path[self.path[:, 0] <= t]
        if len(trail) > 1:
            pts = np.array([self.px(x, y) for _, x, y, _ in trail[::3]], np.int32)
            cv2.polylines(img, [pts], False, (230, 140, 40), 2, cv2.LINE_AA)
        if len(trail):
            _, x, y, yaw = trail[-1]
            c, s_ = math.cos(yaw), math.sin(yaw)
            tri = [(x + 0.35 * c, y + 0.35 * s_), (x - 0.15 * c - 0.15 * s_, y - 0.15 * s_ + 0.15 * c),
                   (x - 0.15 * c + 0.15 * s_, y - 0.15 * s_ - 0.15 * c)]
            cv2.fillPoly(img, [np.array([self.px(*p) for p in tri], np.int32)], (230, 140, 40), cv2.LINE_AA)
        wp = [w for w in self.waypoints if w[0] <= t]
        if wp and t - wp[-1][0] < 0.5:
            _, pts, target = wp[-1]
            if len(pts) > 1:
                cv2.polylines(img, [np.array([self.px(x, y) for x, y in pts], np.int32)], False,
                              (200, 40, 200), 2, cv2.LINE_AA)
            for x, y in pts[1:]:
                cv2.circle(img, self.px(x, y), 4, (200, 40, 200), -1, cv2.LINE_AA)
            if target is not None:
                cv2.circle(img, self.px(*target), 8, (0, 0, 220), 2, cv2.LINE_AA)
        k = sum(c <= t for c in self.closures)
        cv2.rectangle(img, (0, 0), (PANEL_W, 26), (0, 0, 0), -1)
        wp_text = ' | waypoints (magenta), lookahead (red ring)' if self.waypoints else ''
        if self.slam:
            text = (f'RTAB-Map map | loop closures {k} | mapped cones {n} (orange), true cones (green rings), '
                    f'path (blue){wp_text}')
        else:
            text = (f'Track, top view (ground truth){" on RTAB-Map occupancy map" if self.background else ""} | '
                    f'cones (green rings), path (blue){wp_text}')
        cv2.putText(img, text, (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5 if len(text) < 130 else 0.45,
                    (255, 255, 255), 1, cv2.LINE_AA)
        return img


def load_waypoints(path, poses):
    """Classical follower waypoints from its debug log, in the panel's frame.

    Each row (cone_policy_node debug_csv): t;x;y;yaw;v;yaw_rate;fallback;a_v;a_steer;target;path;cones,
    with the path and target in base_link of the (latency-predicted) pose. They are placed with the
    car's pose in the panel frame at that time (`poses`: t, x, y, yaw), so they line up with the
    drawn car whatever odometry drift there is.
    """
    if not path.exists() or not len(poses):
        return []
    import ast
    out = []
    for line in open(path):
        f = line.rstrip('\n').split(';')
        if len(f) < 11:
            continue
        try:
            t = float(f[0])
            pts = np.array(ast.literal_eval(f[10]), float).reshape(-1, 2)
            target = None if f[9] in ('None', '') else np.array(ast.literal_eval(f[9]), float)
        except (ValueError, SyntaxError):
            continue
        k = int(np.argmin(abs(poses[:, 0] - t)))
        if abs(poses[k, 0] - t) > 0.3:
            continue
        _, x, y, yaw = poses[k]
        c, s_ = math.cos(yaw), math.sin(yaw)
        R = np.array([[c, -s_], [s_, c]])
        out.append((t, pts @ R.T + (x, y), None if target is None else R @ target + (x, y)))
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    background = None
    if '--map-from' in argv:
        k = argv.index('--map-from'); background = argv[k + 1]; del argv[k:k + 2]
    run, out = Path(argv[0]), argv[1]
    rows = list(csv.reader(open(run / 'log.csv')))[1:]
    gt = np.array([[float(r[0]), float(r[2]), float(r[3]), float(r[4])] for r in rows if r[1] == 'gt'])
    frames = [(float(r[0]), int(r[2])) for r in rows if r[1] == 'frame']
    chase = []
    if (run / 'chase' / 'stamps.csv').exists():
        chase = [(float(r['t']), int(r['frame'])) for r in csv.DictReader(open(run / 'chase' / 'stamps.csv'))]
    else:
        print('no chase camera frames (record with CHASE=1); onboard view only')
    ct = np.array([c[0] for c in chase])
    moving = np.where(np.hypot(*np.diff(gt[:, 1:3], axis=0).T) > 0.005)[0]
    t0 = gt[moving[0], 0] if len(moving) else gt[0, 0]
    t_end = gt[moving[-1] + 1, 0] + 2.0 if len(moving) else gt[-1, 0]   # stop 2 s after the car last moved
    # start-line crossings (forwards, bottom straight) -> lap times
    cross = [gt[k, 0] for k in range(1, len(gt)) if abs(gt[k, 2]) < 1.5 and gt[k - 1, 1] < START_X <= gt[k, 1]]
    panel = None
    records = map_records(run)
    if records or (run / 'follower.csv').exists():
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src' / 'saurcon_rl'))
        from saurcon_rl.track import Track
        import re
        found = re.search(r'(?<![\w\]])(/[^\s:\[\]@"]+\.world)', open(run / 'launch.log', errors='ignore').read())
        world = found.group(1) if found else None
        panel = MapPanel(run, Track.from_world(world or str(Path(__file__).resolve().parents[2] /
                                                              'src/middle_earth/worlds/racetrack.world')).cones, records,
                         background)
    fx = 320 / math.tan(1.204 / 2)
    det = ConeDetector(fx, fx, 320, 200, camera_height=0.137)
    writer = None
    for ts, idx in frames:
        if ts < t0 - 1.0 or ts > t_end:
            continue
        onboard = cv2.imread(str(run / 'frames' / f'{idx:06d}.jpg'))
        if onboard is None:
            continue
        side = None
        if len(ct):
            j = int(np.argmin(abs(ct - ts)))
            side = cv2.imread(str(run / 'chase' / f'{chase[j][1]:06d}.jpg'))
            if side is None:
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
        frame = onboard if side is None else np.hstack([onboard, side])
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 28), (0, 0, 0), -1)
        cv2.putText(frame, f'Gazebo  t {ts - t0:6.2f}s   v {v:4.1f} m/s   laps {laps}{last}   '
                           f'onboard OAK-D + cone detections' + ('' if side is None else ' | chase camera'),
                    (10, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        if panel is not None:
            p = panel.render(ts)
            if p.shape[1] != frame.shape[1]:
                p = cv2.resize(p, (frame.shape[1], int(round(p.shape[0] * frame.shape[1] / p.shape[1]))))
            frame = np.vstack([frame, p])
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
