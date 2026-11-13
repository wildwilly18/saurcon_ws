"""Raceway geometry: centreline, gates and the drivable corridor.

The centreline matches src/middle_earth/scripts/add_cone_gates.py. Gates are read
from the world file's generated cone gates, so the corridor follows the cones.
Coordinates are the Gazebo world frame.
"""
import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

CONE = re.compile(r'<name>(cone_gate_[^<]+)_([ab])</name>\s*<pose>([^<]+)</pose>')
WORLD = re.compile(r'<world name="([^"]+)"')
CAR_HALF_WIDTH = 0.11     # m, wheel track 0.165 m plus tyres
CONE_RADIUS = 0.018       # m, half the 36 mm base
MARGIN = 0.03             # m


def centreline_points(world, step=0.01):
    pts = []
    if world == 'warehouse_racetrack':
        def line(x0, y0, x1, y1):
            n = int(math.hypot(x1 - x0, y1 - y0) / step)
            pts.extend((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n))
        def arc(cx, cy, r, a0, a1):
            n = int(abs(a1 - a0) * r / step)
            pts.extend((cx + r * math.cos(a0 + (a1 - a0) * i / n),
                        cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n))
        line(-10.5, 0, 7, 0); arc(7, 2, 2, -math.pi / 2, math.pi / 2)
        line(7, 4, -10.5, 4); arc(-10.5, 2, 2, math.pi / 2, 3 * math.pi / 2)
    elif world == 'basement':
        n = int(2 * math.pi * 4.0 / step)
        pts = [(4.5 * math.cos(2 * math.pi * i / n), 3.5 * math.sin(2 * math.pi * i / n)) for i in range(n)]
    else:
        raise ValueError(f'no centreline for world {world}')
    return np.array(pts)


@dataclass
class Track:
    name: str
    xy: np.ndarray          # (N, 2) centreline, counter-clockwise
    s: np.ndarray           # (N,) arc length at each point
    length: float
    heading: np.ndarray     # (N,) tangent direction
    curvature: np.ndarray   # (N,) signed curvature (1/m)
    half_width: float       # allowed |lateral offset| of the car centre
    gates_s: np.ndarray     # arc length of every gate, sorted
    cones: np.ndarray       # (M, 2) cone positions

    @classmethod
    def from_world(cls, path, reverse=False):
        text = Path(path).read_text()
        name = WORLD.search(text).group(1)
        xy = centreline_points(name)
        if reverse:
            xy = xy[::-1].copy()
        d = np.diff(np.vstack([xy, xy[:1]]), axis=0)
        seg = np.hypot(d[:, 0], d[:, 1])
        s = np.concatenate([[0.0], np.cumsum(seg)[:-1]])
        heading = np.arctan2(d[:, 1], d[:, 0])
        dh = np.diff(np.unwrap(np.concatenate([heading, heading[:1]])))
        curvature = np.convolve(dh / seg, np.ones(25) / 25, mode='same')
        pairs = {}
        for gate, side, pose in CONE.findall(text):
            x, y = (float(v) for v in pose.split()[:2])
            pairs.setdefault(gate, {})[side] = (x, y)
        widths, gs, cones = [], [], []
        for p in pairs.values():
            (ax, ay), (bx, by) = p['a'], p['b']
            widths.append(math.hypot(ax - bx, ay - by))
            gs.append(s[np.argmin(np.hypot(xy[:, 0] - (ax + bx) / 2, xy[:, 1] - (ay + by) / 2))])
            cones += [p['a'], p['b']]
        if not widths:
            raise ValueError(f'{path}: no cone gates')
        half = min(widths) / 2 - CONE_RADIUS - CAR_HALF_WIDTH - MARGIN
        return cls(name + ('_reverse' if reverse else ''), xy, s, float(s[-1] + seg[-1]), heading,
                   curvature, half, np.sort(gs), np.array(cones))

    def project(self, x, y, hint=None, window=400):
        """Nearest centreline index for (x, y); searches near `hint` if given."""
        if hint is None:
            return int(np.argmin((self.xy[:, 0] - x) ** 2 + (self.xy[:, 1] - y) ** 2))
        idx = (hint + np.arange(-window // 4, window)) % len(self.xy)
        return int(idx[np.argmin((self.xy[idx, 0] - x) ** 2 + (self.xy[idx, 1] - y) ** 2)])

    def frenet(self, x, y, yaw, i):
        """Lateral offset (left +) and heading error at centreline index i."""
        h = self.heading[i]
        dx, dy = x - self.xy[i, 0], y - self.xy[i, 1]
        e = -math.sin(h) * dx + math.cos(h) * dy
        dpsi = math.atan2(math.sin(yaw - h), math.cos(yaw - h))
        return e, dpsi

    def ahead(self, i, distances):
        """Centreline indices at arc distances ahead of index i."""
        target = (self.s[i] + np.asarray(distances)) % self.length
        return np.searchsorted(self.s, target) % len(self.s)
