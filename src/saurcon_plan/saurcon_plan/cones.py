"""Cone detection and cone mapping, shared by the Gazebo node and the MuJoCo pipeline.

Detection (per image): threshold the cone colour in HSV, then keep blobs that are
cone-shaped in metres. Range, in order of preference:
  depth  - median of the blob's valid pixels in the aligned depth image;
  ground - where the cone's base meets a flat floor, for a camera at a known
           height: Z = fy * camera_height / (v_base + row_offset - cy). Measured on
           Gazebo frames: 3-8 cm median error out to 6.5 m;
  size   - the known cone height: Z = fy * h_cone / h_pixels. Only ~0.4 m accurate at
           2-6 m (a cone is ~8 px tall at 4 m and the colour mask often misses its base).
Filters: blob bottom below the image horizon (cones sit on the floor, below the
camera), physical height 0.03-0.12 m, width <= 0.07 m, taller than wide.

Mapping: detections are transformed into the map frame by the caller (with any
pose source) and associated to the nearest existing cone within `assoc_radius`;
the position is a running mean weighted by 1/range^2 (near sightings are more
accurate). A cone is confirmed after `min_hits` sightings.
"""
from dataclasses import dataclass, field

import cv2
import numpy as np

CONE_HEIGHT = 0.071      # m, 1:10 traffic cone (rc_cone model)


@dataclass
class Detection:
    u: float                 # pixel column of the blob's base centre
    v: float                 # pixel row of the blob's base
    p_cam: np.ndarray        # cone base point in the camera optical frame (x right, y down, z forward), m
    range: float
    method: str              # 'depth' or 'size'
    height_m: float
    width_m: float


@dataclass
class ConeDetector:
    fx: float
    fy: float
    cx: float
    cy: float
    hsv_lo: tuple = (15, 150, 110)       # Gazebo cones (racks are hue 7-8)
    hsv_hi: tuple = (32, 255, 255)
    min_px: int = 5                      # blob height in pixels (sets maximum range)
    max_range: float = 6.5               # the cone policy is trained on cones out to 6.5 m
    camera_height: float = None          # m above the floor; enables ground-plane ranging
    row_offset: float = 1.0              # px; blob bottom sits ~1 px above the contact (fitted)

    def detect(self, bgr, depth_m=None):
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_lo, self.hsv_hi)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        n, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        out = []
        for i in range(1, n):
            x, y, w, h, area = stats[i]
            if h < self.min_px or y + h - 1 <= self.cy or h < 1.1 * w:
                continue
            Z, method = None, 'size'
            if depth_m is not None:
                d = depth_m[labels == i]
                d = d[np.isfinite(d) & (d > 0.05)]
                if len(d) >= 3:
                    Z, method = float(np.median(d)), 'depth'
            v_base = float(y + h - 1)
            if Z is None and self.camera_height and v_base + self.row_offset - self.cy > 1:
                Z, method = self.fy * self.camera_height / (v_base + self.row_offset - self.cy), 'ground'
            if Z is None:
                Z = self.fy * CONE_HEIGHT / h
            height_m, width_m = h * Z / self.fy, w * Z / self.fx
            if not (0.03 <= height_m <= 0.12 and width_m <= 0.07 and Z <= self.max_range):
                continue
            u, v = x + w / 2.0, float(y + h - 1)
            p = np.array([(u - self.cx) * Z / self.fx, (v - self.cy) * Z / self.fy, Z])
            out.append(Detection(u, v, p, float(np.linalg.norm(p)), method, height_m, width_m))
        return out


@dataclass
class ConeMap:
    assoc_radius: float = 0.25
    min_hits: int = 3
    xy: list = field(default_factory=list)      # running means
    w: list = field(default_factory=list)       # accumulated weights
    hits: list = field(default_factory=list)

    def update(self, points_xy, ranges):
        for p, r in zip(np.asarray(points_xy).reshape(-1, 2), ranges):
            wt = 1.0 / max(r, 0.3) ** 2
            if self.xy:
                d = np.hypot(*(np.array(self.xy) - p).T)
                j = int(np.argmin(d))
                if d[j] < self.assoc_radius:
                    W = self.w[j] + wt
                    self.xy[j] = (self.xy[j] * self.w[j] + p * wt) / W
                    self.w[j] = W; self.hits[j] += 1
                    continue
            self.xy.append(np.array(p, float)); self.w.append(wt); self.hits.append(1)

    def cones(self):
        """Confirmed cone positions, (N, 2)."""
        keep = [p for p, h in zip(self.xy, self.hits) if h >= self.min_hits]
        return np.array(keep).reshape(-1, 2)


def score(mapped_xy, true_xy, match_radius=0.2):
    """Precision, recall and RMS position error of a cone map against the true cones."""
    mapped_xy, true_xy = np.asarray(mapped_xy).reshape(-1, 2), np.asarray(true_xy).reshape(-1, 2)
    used, errs = set(), []
    for p in mapped_xy:
        d = np.hypot(*(true_xy - p).T)
        for j in np.argsort(d):
            if d[j] > match_radius:
                break
            if j not in used:
                used.add(int(j)); errs.append(d[j]); break
    tp = len(errs)
    return {'mapped': len(mapped_xy), 'true': len(true_xy), 'matched': tp,
            'precision': round(tp / max(len(mapped_xy), 1), 3), 'recall': round(tp / max(len(true_xy), 1), 3),
            'rms_m': round(float(np.sqrt(np.mean(np.square(errs)))) if errs else float('nan'), 3),
            'max_m': round(float(np.max(errs)) if errs else float('nan'), 3)}


def planar(pose_xy_yaw, p_base_xy):
    """Transform (N, 2) points from a planar body frame into the parent frame."""
    x, y, yaw = pose_xy_yaw
    c, s = np.cos(yaw), np.sin(yaw)
    p = np.asarray(p_base_xy).reshape(-1, 2)
    return np.column_stack([x + c * p[:, 0] - s * p[:, 1], y + s * p[:, 0] + c * p[:, 1]])
