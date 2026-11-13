"""Classical cone follower: centreline from cone gates, pure pursuit, curvature speed profile.

SAURCON's driving planner for the cone track, and the baseline the cone-vision RL policies
(trained in MuJoCo, saurcon_rl) are measured against. Input: the cone memory
(saurcon_plan.memory.ConeMemory) expressed in base_link (x forward, y left, origin at the rear
axle), plus the measured speed. No map, no localization, no learning. It runs on the car or in
Gazebo through cone_follower_node, and in MuJoCo through saurcon_rl.cone_drive.

1. Centreline. Delaunay-triangulate the remembered cones. An edge between the two cones of
   a gate (or between cones of neighbouring gates on opposite sides) is gate_width long; an
   edge along one boundary is shorter (cones 0.2-1.2 m apart) or is not a Delaunay edge at
   all. Midpoints of edges between `min_gate` and `max_gate` long are therefore points on
   the centreline.
2. Path. From the rear axle, chain the midpoints greedily forward: the next point is the
   nearest one 0.15-2.5 m ahead within 70 deg of the current direction. The chain is the
   path to follow, out to however far the car can see.
3. Steering. Pure pursuit from the rear axle (base_link):  delta = atan(2 L sin(alpha) / ld),
   target ld = lookahead along the path, ld growing with speed. Optionally the target is
   taken from the pose `latency` seconds ahead (constant speed and yaw rate), which
   cancels a known sensing/actuation delay.
4. Speed. The tightest curvature over the path ahead sets the cornering speed
   v = sqrt(a_lat / kappa); braking a_brake bounds how fast one may approach it, and the
   car must be able to stop within the path it can see (no cones seen -> slow down).
"""
import math
from dataclasses import dataclass, field

import numpy as np
from scipy.spatial import Delaunay

from .vehicle import STEER_MAX, V_MAX, WHEELBASE


@dataclass
class ConeFollower:
    # Cone-to-cone edges treated as crossing the track: the 2.2 m gates, and diagonals to the
    # neighbouring gate (up to ~2.5 m). Tighter than it looks necessary: the inner cones of the two
    # straights are only 1.8 m apart and must not be paired (that put midpoints in the infield).
    min_gate: float = 1.95         # m
    max_gate: float = 2.75         # m
    lookahead_min: float = 0.7     # m
    lookahead_gain: float = 0.3    # s: lookahead = min + gain * v
    lookahead_max: float = 2.2     # m
    a_lat: float = 5.0             # m/s^2 allowed lateral acceleration (grip is ~10)
    a_brake: float = 2.5           # m/s^2 planned braking (the car can do 4; curves are seen late)
    v_max: float = 5.0             # m/s
    v_min: float = 0.6             # m/s: keep creeping forward while the path is short
    v_fallback: float = 2.5        # m/s cap while following a single boundary (inner cones unseen)
    latency: float = 0.0           # s: predict the pose this far ahead before steering
    path: np.ndarray = field(default_factory=lambda: np.zeros((0, 2)))
    mids: np.ndarray = field(default_factory=lambda: np.zeros((0, 2)))
    target: tuple = None
    edge_dirs: np.ndarray = field(default_factory=lambda: np.zeros((0, 2)))
    clearance: np.ndarray = None   # per midpoint: distance to the nearest cone
    min_clearance: float = 0.6     # m; a centreline point is ~1.1 m (half a gate) from every cone
    fallback: bool = False         # this step's path came from one boundary
    last: tuple = (0.0, 0.0)       # last (speed, steering) command, held while the path is lost
    lost_steps: int = 0            # consecutive steps without a path
    stop_after: int = 20           # steps (1 s at 20 Hz) without a path -> stop
    # How long the cone memory feeding the follower keeps a cone after its last sighting. The
    # inner cones of a tight bend leave the +/-33 deg view well before the car passes them; at
    # bend speed (~2 m/s) the RL policies' 2 s memory forgot them first, leaving no gates and
    # only the outer boundary (feature warehouse, 3 m bend). The follower ignores cone ages,
    # and odometry drifts millimetres over a few seconds, so it can remember longer.
    memory_s: float = 5.0

    # -- geometry ---------------------------------------------------------------------------
    def midpoints(self, cones):
        cones = np.asarray(cones, float).reshape(-1, 2)
        if len(cones) < 3:
            return np.zeros((0, 2))
        try:
            tri = Delaunay(cones)
        except Exception:          # collinear or duplicate points
            return np.zeros((0, 2))
        edges = set()
        for a, b, c in tri.simplices:
            edges |= {tuple(sorted(e)) for e in ((a, b), (b, c), (a, c))}
        mids, dirs = [], []
        for i, j in edges:
            v = cones[j] - cones[i]
            d = np.hypot(*v)
            if self.min_gate <= d <= self.max_gate:
                mids.append((cones[i] + cones[j]) / 2); dirs.append(v / d)
        self.edge_dirs = np.array(dirs).reshape(-1, 2)
        mids = np.array(mids).reshape(-1, 2)
        # distance from each midpoint to the nearest cone
        self.clearance = (np.hypot(*(mids[:, None, :] - cones[None, :, :]).transpose(2, 0, 1)).min(axis=1)
                          if len(mids) else np.zeros(0))
        return mids

    def chain(self, mids, start=(0.0, 0.0), heading=0.0):
        pts, cur, h = [np.array(start, float)], np.array(start, float), heading
        left = list(range(len(mids)))
        while left:
            best, best_cost = None, math.inf
            for k in left:
                d = mids[k] - cur
                r = math.hypot(*d)
                if not 0.15 < r < 2.5:
                    continue
                ang = abs((math.atan2(d[1], d[0]) - h + math.pi) % (2 * math.pi) - math.pi)
                if ang > math.radians(70):
                    continue
                # the edge must cross the track: within 50 deg of perpendicular to the chain's
                # heading (a gate, or a diagonal to a nearby gate). An edge along one boundary
                # (two cones of one side whose neighbours were missed) runs with the track and
                # would put a midpoint on the boundary. Test against the heading, not against the
                # direction to the midpoint: a boundary chord right beside the car is seen at a
                # steep angle and passed that test (feature warehouse, 0.65 m gate spacing).
                if abs(self.edge_dirs[k] @ (math.cos(h), math.sin(h))) > math.cos(math.radians(50)):
                    continue
                if abs(np.dot(self.edge_dirs[k], d / r)) > math.cos(math.radians(50)):
                    continue
                if self.clearance is not None and self.clearance[k] < self.min_clearance:
                    continue                # a centreline point is ~half a gate from every cone
                cost = r + 1.5 * ang
                if cost < best_cost:
                    best, best_cost = k, cost
            if best is None:
                break
            nxt = mids[best]
            h = math.atan2(*(nxt - cur)[::-1])
            # drop midpoints now behind or beside the chain (duplicates from diagonals)
            left = [k for k in left if k != best and np.dot(mids[k] - nxt, (math.cos(h), math.sin(h))) > 0.05]
            pts.append(nxt); cur = nxt
        return np.array(pts)

    def boundary_path(self, cones, width=2.2):
        """Fallback when no gates are seen: follow one boundary, offset half a track width.

        In the bends the camera (+/-33 deg) often sees only the outer cones; the inner ones are
        beside the car. Chain the cones ahead along the boundary and shift the chain by
        width / 2 towards the side the car is on (the car is inside the track).
        """
        cones = np.asarray(cones, float).reshape(-1, 2)
        ahead = cones[(cones[:, 0] > -0.3) & (np.hypot(cones[:, 0], cones[:, 1]) < 6.5)]
        if len(ahead) < 2:
            return np.zeros((0, 2))
        best = None
        for start in np.argsort(np.hypot(ahead[:, 0], ahead[:, 1]))[:3]:
            chain, cur, h, left = [ahead[start]], ahead[start], 0.0, [k for k in range(len(ahead)) if k != start]
            while left:
                d = ahead[left] - cur; r = np.hypot(d[:, 0], d[:, 1])
                ang = np.abs((np.arctan2(d[:, 1], d[:, 0]) - h + np.pi) % (2 * np.pi) - np.pi)
                ok = (r > 0.1) & (r < 1.6) & (ang < np.radians(60))
                if not ok.any():
                    break
                k = int(np.flatnonzero(ok)[np.argmin((r + ang)[ok])])
                nxt = ahead[left[k]]; h = math.atan2(*(nxt - cur)[::-1])
                chain.append(nxt); cur = nxt; left.pop(k)
            if len(chain) >= 2 and (best is None or len(chain) > len(best)):
                best = chain
        if best is None:
            return np.zeros((0, 2))
        b = np.array(best)
        # Smooth the chain (3-point moving average) and offset it along normals from central
        # differences: remembered cones are noisy and, with dense gates, closely spaced, so
        # offsetting each short segment on its own made a zig-zag path that touched cones.
        if len(b) >= 3:
            b = np.vstack([b[:1], (b[:-2] + b[1:-1] + b[2:]) / 3, b[-1:]])
        tan = np.gradient(b, axis=0)
        tan /= np.maximum(np.hypot(tan[:, 0], tan[:, 1]), 1e-6)[:, None]
        normal = np.column_stack([-tan[:, 1], tan[:, 0]])          # left of the boundary direction
        side = np.sign(tan[0, 0] * -b[0, 1] - tan[0, 1] * -b[0, 0]) or 1.0   # the car (origin) is on this side
        offs = b + side * normal * width / 2
        # keep points ahead of the car that make forward progress along the boundary
        keep, last = [], None
        for p, t in zip(offs, tan):
            if p[0] <= 0.1:
                continue
            if last is not None and np.dot(p - last, t) <= 0.05:
                continue
            keep.append(p); last = p
        return np.vstack([[0.0, 0.0], keep]) if keep else np.zeros((0, 2))

    @staticmethod
    def along(path, dist):
        """Point at arc length `dist` along a polyline.

        dist <= 0 gives the first point; beyond the end the last non-degenerate segment is
        extended. Zero-length segments (repeated points) are skipped. A path of one point, or of
        only repeated points, extends along +x from its first point.
        """
        path = np.asarray(path, float)
        seg = np.hypot(*np.diff(path, axis=0).T)
        keep = np.flatnonzero(seg > 1e-9)
        if not len(keep):
            return path[0] + (max(dist, 0.0), 0.0)
        if dist <= 0.0:
            return path[0].copy()
        s = np.concatenate([[0.0], np.cumsum(seg)])
        if dist >= s[-1]:
            k = keep[-1]
            d = (path[k + 1] - path[k]) / seg[k]
            return path[-1] + d * (dist - s[-1])
        # segment k spans s[k] .. s[k+1]; side='right' keeps k in 0..len(seg)-1 for 0 < dist < s[-1]
        k = int(np.searchsorted(s, dist, side='right')) - 1
        while seg[k] <= 1e-9:                     # dist exactly at a repeated point
            k += 1
        f = (dist - s[k]) / seg[k]
        return path[k] + f * (path[k + 1] - path[k])

    @staticmethod
    def max_curvature(path, step=0.4, horizon=4.0):
        """Largest curvature of circles through points `step` apart over the path ahead."""
        seg = np.hypot(*np.diff(path, axis=0).T)
        length = float(np.sum(seg))
        kmax, dist_at = 0.0, 0.0
        s = step
        while s + step <= min(length, horizon):
            a, b, c = (ConeFollower.along(path, s - step), ConeFollower.along(path, s), ConeFollower.along(path, s + step))
            ab, bc, ca = np.hypot(*(b - a)), np.hypot(*(c - b)), np.hypot(*(a - c))
            area2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
            k = 2 * area2 / max(ab * bc * ca, 1e-9)
            if k > kmax:
                kmax, dist_at = k, s
            s += step / 2
        return kmax, dist_at, length

    # -- control ----------------------------------------------------------------------------
    def act(self, cones_base, v, yaw_rate=0.0):
        """cones in base_link (N, 2), speed (m/s) -> (speed command m/s, steering angle rad)."""
        self.mids = self.midpoints(cones_base)
        self.path = self.chain(self.mids)
        self.fallback = False
        length = float(np.sum(np.hypot(*np.diff(self.path, axis=0).T))) if len(self.path) > 1 else 0.0
        if length < 1.0:                       # no gates ahead: follow a single boundary
            alt = self.boundary_path(cones_base)
            if len(alt) >= 2:
                self.path, self.fallback = alt, True
        # pose after the latency, in the current base_link frame
        dt = self.latency
        yaw_p = yaw_rate * dt
        px, py = (v * dt * math.cos(yaw_p / 2), v * dt * math.sin(yaw_p / 2))
        ld = float(np.clip(self.lookahead_min + self.lookahead_gain * v, self.lookahead_min, self.lookahead_max))
        if len(self.path) < 2:
            # path lost for a moment (cones missed): hold the last steering, slow down;
            # lost for longer (off the track, nothing to follow): stop
            self.lost_steps += 1
            v_cmd = 0.0 if self.lost_steps > self.stop_after else max(self.v_min, min(self.last[0], v) * 0.85)
            self.last = (v_cmd, self.last[1]); self.target = None
            return self.last
        self.lost_steps = 0
        base = math.hypot(px, py)
        tx, ty = self.along(self.path, ld + base)     # lookahead along the path from the predicted pose
        c, s = math.cos(yaw_p), math.sin(yaw_p)
        dx, dy = tx - px, ty - py
        lx, ly = c * dx + s * dy, -s * dx + c * dy
        alpha = math.atan2(ly, lx)
        dist = max(math.hypot(lx, ly), 0.3)
        steer = float(np.clip(math.atan2(2 * WHEELBASE * math.sin(alpha), dist), -STEER_MAX, STEER_MAX))
        self.target = (tx, ty)
        # speed
        kmax, d_k, length = self.max_curvature(self.path)
        v_corner = math.sqrt(self.a_lat / max(kmax, 1e-3))
        v_ok = math.sqrt(v_corner ** 2 + 2 * self.a_brake * d_k)
        v_stop = math.sqrt(2 * self.a_brake * max(length - 0.3, 0.0))   # stop within what is seen
        v_steer = math.sqrt(self.a_lat * WHEELBASE / max(abs(math.tan(steer)), 1e-3))
        v_cap = self.v_fallback if self.fallback else self.v_max
        v_cmd = float(np.clip(min(v_cap, v_ok, v_stop, v_steer), self.v_min, V_MAX))
        self.last = (v_cmd, steer)
        return v_cmd, steer

    def action(self, cones_base, v, yaw_rate=0.0):
        """Same, as the normalised action the RL environments take: [speed, steering] in -1..1."""
        v_cmd, steer = self.act(cones_base, v, yaw_rate)
        return np.array([v_cmd / V_MAX * 2 - 1, steer / STEER_MAX], np.float32)
