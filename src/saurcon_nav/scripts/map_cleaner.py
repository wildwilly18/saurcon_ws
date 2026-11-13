#!/usr/bin/env python3
"""Clean RTAB-Map's occupancy grid (/map -> /map_clean) and build a drivable map (/map_drivable).

With ray tracing, RTAB-Map marks free the cells its depth rays cross. Rays from successive
map nodes do not cover every 5 cm cell, so observed free space is speckled with single unknown
cells (1,582 one-cell and 203 two-to-four-cell holes in a 3-lap feature-warehouse map).

Rule: an unknown region (8-connected) of at most `max_hole_cells` cells whose every
neighbouring cell is free becomes free. A hole touching an occupied cell, the map edge or the
large unknown area is left alone, so the frontier and obstacles are never changed and no free
space is invented beyond what surrounds the hole. Occupied cells are never changed: isolated
ones are rare and may be real thin objects (a cone's base is under one cell).

Drivable map (/map_drivable, when a cone map is available): the area inside the cone corridor
is open (0) and everything outside it is not (100); see `drivable_grid`. Built from the mapped
cones (/cones_rtab/map, cone_mapping:=rtab) and the path RTAB-Map's graph drove
(/rtabmap/mapPath), both in the map frame. Obstacles RTAB-Map saw inside the corridor stay 100.

The raw /map is untouched; /map_clean and /map_drivable are separate topics for display and
planners. `clean_grid` and `drivable_grid` are pure functions, also used by
scripts/sim_eval/make_race_video.py.
"""
import numpy as np

UNKNOWN = -1
FREE_MAX = 49            # OccupancyGrid values 0..49 count as free (RTAB-Map publishes 0 / 100 / -1)


def clean_grid(data, max_hole_cells=8):
    """data: (H, W) int array, OccupancyGrid values (-1 unknown, 0..100). Returns (cleaned, filled)."""
    import cv2
    data = np.asarray(data)
    unknown = (data == UNKNOWN).astype(np.uint8)
    free = (data >= 0) & (data <= FREE_MAX)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(unknown, connectivity=8)
    out = data.copy()
    filled = 0
    H, W = data.shape
    for k in range(1, n):
        x, y, w, h, area = stats[k]
        if area > max_hole_cells or x == 0 or y == 0 or x + w >= W or y + h >= H:
            continue                                     # large, or touches the map edge
        sl = (slice(y - 1, y + h + 1), slice(x - 1, x + w + 1))
        hole = lab[sl] == k
        ring = cv2.dilate(hole.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~hole
        if free[sl][ring].all():
            out[sl][hole] = 0
            filled += int(area)
    return out, filled


def drivable_grid(data, origin, res, path_xy, cones_xy, keep_obstacles=True,
                  min_half=0.5, max_half=1.8, reach=3.0, window=1.0):
    """Drivable map from the cone layout: inside the cone corridor 0 (open), outside 100 (not).

    data: (H, W) OccupancyGrid values (row 0 at origin y); origin (x, y) of cell (0, 0)'s corner;
    res: m per cell; path_xy: (N, 2) path the car drove (map frame); cones_xy: (M, 2) mapped
    cones (map frame).

    The path tells left from right: each cone is assigned to its nearest path point and its
    signed lateral offset taken (cones 0.5-1.8 m to the side are kept; duplicates and stray
    detections farther off are not). At every path point the corridor reaches from the median
    right-cone offset to the median left-cone offset of cones within +/- `window` m along the
    path (interpolated where a side has none). A cell is drivable if its nearest path point is
    within `reach` m and its lateral offset lies inside that interval. Cones facing each other
    across an infield are never paired, because no driven path runs between them. With
    keep_obstacles, cells RTAB-Map saw occupied stay 100 even inside the corridor (a fallen
    cone or other obstacle in the lane). Returns (grid, None) or (None, reason).
    """
    from scipy.spatial import cKDTree
    data = np.asarray(data)
    path = np.asarray(path_xy, float).reshape(-1, 2)
    cones = np.asarray(cones_xy, float).reshape(-1, 2)
    if len(path) < 2 or len(cones) < 4:
        return None, 'need a driven path and at least 4 cones'
    # resample the path every 0.1 m
    seg = np.hypot(*np.diff(path, axis=0).T)
    path = path[np.concatenate([[True], seg > 1e-6])]
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(path, axis=0).T))])
    if s[-1] < 1.0:
        return None, 'path too short'
    t = np.arange(0.0, s[-1], 0.1)
    p = np.column_stack([np.interp(t, s, path[:, 0]), np.interp(t, s, path[:, 1])])
    tan = np.gradient(p, axis=0); tan /= np.maximum(np.hypot(*tan.T), 1e-9)[:, None]
    nrm = np.column_stack([-tan[:, 1], tan[:, 0]])          # left of the direction of travel
    tree = cKDTree(p)
    # lateral offset of each cone from its nearest path point
    _, k = tree.query(cones)
    e = np.einsum('ij,ij->i', cones - p[k], nrm[k])
    ok = (np.abs(e) >= min_half) & (np.abs(e) <= max_half)
    k, e = k[ok], e[ok]
    w = int(round(window / 0.1))
    left = np.full(len(p), np.nan); right = np.full(len(p), np.nan)
    for i in range(len(p)):
        near = np.abs(k - i) <= w
        l, r = e[near & (e > 0)], e[near & (e < 0)]
        if len(l):
            left[i] = np.median(l)
        if len(r):
            right[i] = -np.median(r)
    for arr in (left, right):
        good = ~np.isnan(arr)
        if not good.any():
            return None, 'cones on only one side of the path'
        arr[~good] = np.interp(np.flatnonzero(~good), np.flatnonzero(good), arr[good])
    # cells near the path: inside the corridor?
    H, W = data.shape
    out = np.full((H, W), 100, np.int16)
    x0, y0 = origin
    c0 = max(int((p[:, 0].min() - reach - x0) / res), 0); c1 = min(int((p[:, 0].max() + reach - x0) / res) + 1, W)
    r0 = max(int((p[:, 1].min() - reach - y0) / res), 0); r1 = min(int((p[:, 1].max() + reach - y0) / res) + 1, H)
    if c1 <= c0 or r1 <= r0:
        return out, None
    cc, rr = np.meshgrid(np.arange(c0, c1), np.arange(r0, r1))
    xy = np.column_stack([x0 + (cc.ravel() + 0.5) * res, y0 + (rr.ravel() + 0.5) * res])
    d, j = tree.query(xy, distance_upper_bound=reach)
    near = np.isfinite(d)
    inside = np.zeros(len(xy), bool)
    jj = j[near]
    lat = np.einsum('ij,ij->i', xy[near] - p[jj], nrm[jj])
    inside[near] = (lat <= left[jj]) & (lat >= -right[jj])
    block = out[r0:r1, c0:c1]
    block[inside.reshape(block.shape)] = 0
    if keep_obstacles:
        out[(data > FREE_MAX)] = 100
    return out, None


def main():
    import rclpy
    from geometry_msgs.msg import PoseArray
    from nav_msgs.msg import OccupancyGrid, Path
    from rclpy.node import Node
    from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

    class MapCleaner(Node):
        def __init__(self):
            super().__init__('map_cleaner')
            self.max_hole = int(self.declare_parameter('max_hole_cells', 8).value)
            qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                             reliability=ReliabilityPolicy.RELIABLE)
            self.pub = self.create_publisher(OccupancyGrid, '/map_clean', qos)
            self.pub_drv = self.create_publisher(OccupancyGrid, '/map_drivable', qos)
            self.cones, self.path = None, None
            self.create_subscription(OccupancyGrid, '/map', self.on_map, qos)
            self.create_subscription(PoseArray, '/cones_rtab/map', self.on_cones, 10)
            self.create_subscription(Path, '/rtabmap/mapPath', self.on_path, 10)

        def on_cones(self, msg):
            self.cones = np.array([[q.position.x, q.position.y] for q in msg.poses]).reshape(-1, 2)

        def on_path(self, msg):
            self.path = np.array([[q.pose.position.x, q.pose.position.y] for q in msg.poses]).reshape(-1, 2)

        def on_map(self, msg):
            if not rclpy.ok():
                return                              # shutting down: the publishers' context is gone
            data = np.array(msg.data, dtype=np.int16).reshape(msg.info.height, msg.info.width)
            cleaned, filled = clean_grid(data, self.max_hole)
            out = OccupancyGrid(header=msg.header, info=msg.info)
            out.data = cleaned.astype(np.int8).ravel().tolist()
            self.pub.publish(out)
            self.get_logger().info(f'filled {filled} unknown cells in small holes', throttle_duration_sec=30.0)
            if self.cones is not None and self.path is not None:
                o = msg.info.origin.position
                drv, why = drivable_grid(cleaned, (o.x, o.y), msg.info.resolution, self.path, self.cones)
                if drv is None:
                    self.get_logger().info(f'no drivable map yet: {why}', throttle_duration_sec=30.0)
                    return
                d = OccupancyGrid(header=msg.header, info=msg.info)
                d.data = drv.astype(np.int8).ravel().tolist()
                self.pub_drv.publish(d)
                self.get_logger().info(f'drivable map: {int((drv == 0).sum())} open cells from {len(self.cones)} cones',
                                       throttle_duration_sec=30.0)

    rclpy.init()
    node = MapCleaner()
    from rclpy.executors import ExternalShutdownException
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
