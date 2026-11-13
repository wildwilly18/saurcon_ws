"""Short-term cone memory: recently detected cones in a frame that does not move with the car."""
import math

import numpy as np


class ConeMemory:
    """Recently detected cones in a fixed frame (world in simulation, odom on the car).

    update(): merge this frame's detections (same frame) into memory; a detection
    within `merge_radius` of a remembered cone refreshes it (position averaged).
    Cones not seen for `horizon` seconds are forgotten.
    relative(): remembered cones in the given base_link pose, with their ages.

    The classical follower keeps cones 5 s (ConeFollower.memory_s); the RL cone policies were
    trained with 2 s (saurcon_rl.cone_env.MEMORY_S).
    """
    def __init__(self, horizon=2.0, merge_radius=0.3):
        self.horizon, self.merge_radius = horizon, merge_radius
        self.xy = np.zeros((0, 2)); self.seen = np.zeros(0); self.n = np.zeros(0)

    def update(self, points_xy, t):
        for p in np.asarray(points_xy, float).reshape(-1, 2):
            if len(self.xy):
                d = np.hypot(*(self.xy - p).T); j = int(np.argmin(d))
                if d[j] < self.merge_radius:
                    self.xy[j] = (self.xy[j] * self.n[j] + p) / (self.n[j] + 1)
                    self.n[j] = min(self.n[j] + 1, 10); self.seen[j] = t
                    continue
            self.xy = np.vstack([self.xy, p]); self.seen = np.append(self.seen, t); self.n = np.append(self.n, 1)
        keep = t - self.seen <= self.horizon
        self.xy, self.seen, self.n = self.xy[keep], self.seen[keep], self.n[keep]

    def relative(self, x, y, yaw, t):
        c, s = math.cos(yaw), math.sin(yaw)
        d = self.xy - (x, y)
        return np.column_stack([c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1]]), t - self.seen
