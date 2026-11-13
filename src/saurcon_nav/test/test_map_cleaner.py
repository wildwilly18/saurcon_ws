"""map_cleaner.clean_grid: fill only small unknown holes fully surrounded by free cells."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np

spec = importlib.util.spec_from_file_location('map_cleaner', Path(__file__).parents[1] / 'scripts/map_cleaner.py')
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)

U, F, O = -1, 0, 100


def grid(h=12, w=12):
    g = np.full((h, w), U, np.int16)
    g[2:10, 2:10] = F                     # a block of observed free space inside unknown
    return g


class CleanGridTest(unittest.TestCase):
    def test_single_hole_in_free_space_is_filled(self):
        g = grid(); g[5, 5] = U
        out, filled = mc.clean_grid(g)
        self.assertEqual(out[5, 5], F)
        self.assertEqual(filled, 1)

    def test_small_cluster_is_filled_large_is_not(self):
        g = grid(); g[4:6, 4:6] = U        # 4 cells
        self.assertTrue((mc.clean_grid(g)[0][4:6, 4:6] == F).all())
        g = grid(); g[3:6, 3:6] = U        # 9 cells > 8
        self.assertTrue((mc.clean_grid(g)[0][3:6, 3:6] == U).all())
        self.assertTrue((mc.clean_grid(g, max_hole_cells=9)[0][3:6, 3:6] == F).all())

    def test_hole_touching_an_obstacle_is_kept(self):
        g = grid(); g[5, 5] = U; g[5, 6] = O
        out, _ = mc.clean_grid(g)
        self.assertEqual(out[5, 5], U)
        g = grid(); g[5, 5] = U; g[6, 6] = O    # diagonal contact counts too
        self.assertEqual(mc.clean_grid(g)[0][5, 5], U)

    def test_frontier_and_large_unknown_unchanged(self):
        g = grid(); g[2, 5] = U              # a notch in the edge of free space, joined to the outside
        out, filled = mc.clean_grid(g)
        self.assertEqual(out[2, 5], U)
        self.assertEqual(filled, 0)
        self.assertTrue((out[:2] == U).all() and (out[:, :2] == U).all())

    def test_hole_at_map_edge_is_kept(self):
        g = np.full((6, 6), F, np.int16); g[0, 3] = U
        self.assertEqual(mc.clean_grid(g)[0][0, 3], U)

    def test_occupied_cells_never_change(self):
        g = grid(); g[5, 5] = O              # an isolated obstacle cell (could be a cone)
        g[7, 7] = U
        out, _ = mc.clean_grid(g)
        self.assertEqual(out[5, 5], O)
        self.assertTrue(((g == O) == (out == O)).all())


def stadium(step=0.05):
    """Racetrack-like centreline: straights at y=0 and y=4 joined by 2 m radius bends."""
    pts = []
    for x in np.arange(-8, 6, step): pts.append((x, 0.0))
    for a in np.arange(-np.pi / 2, np.pi / 2, step / 2): pts.append((6 + 2 * np.cos(a), 2 + 2 * np.sin(a)))
    for x in np.arange(6, -8, -step): pts.append((x, 4.0))
    for a in np.arange(np.pi / 2, 3 * np.pi / 2, step / 2): pts.append((-8 + 2 * np.cos(a), 2 + 2 * np.sin(a)))
    return np.array(pts)


def gate_cones(path, every=12, half=1.1):
    t = np.gradient(path, axis=0); t /= np.hypot(*t.T)[:, None]
    n = np.column_stack([-t[:, 1], t[:, 0]])
    idx = np.arange(0, len(path), every)
    return np.vstack([path[idx] + half * n[idx], path[idx] - half * n[idx]])


class DrivableTest(unittest.TestCase):
    res, origin = 0.05, (-12.0, -4.0)

    def cell(self, g, x, y):
        return g[int((y - self.origin[1]) / self.res), int((x - self.origin[0]) / self.res)]

    def setUp(self):
        self.data = np.full((240, 400), U, np.int16)              # 20 m x 12 m, all unknown
        self.path = stadium()
        self.cones = gate_cones(self.path)

    def test_inside_open_outside_not(self):
        g, why = mc.drivable_grid(self.data, self.origin, self.res, self.path, self.cones)
        self.assertIsNone(why)
        self.assertEqual(self.cell(g, 0.0, 0.0), 0)           # on the bottom straight (unknown in /map)
        self.assertEqual(self.cell(g, 0.0, 0.9), 0)           # inside, near the left cones
        self.assertEqual(self.cell(g, 0.0, -1.6), 100)        # outside the track
        self.assertEqual(self.cell(g, 7.9, 2.0), 0)           # in the bend
        self.assertEqual(self.cell(g, -10.5, 2.0), 0)         # far bend, between centreline (-10) and outer cones (-11.1)
        self.assertEqual(self.cell(g, -11.6, 2.0), 100)       # beyond the far bend's outer cones

    def test_infield_between_straights_is_not_drivable(self):
        # the inner cones of the two straights are only 1.8 m apart (y = 1.1 and 2.9)
        g, _ = mc.drivable_grid(self.data, self.origin, self.res, self.path, self.cones)
        self.assertEqual(self.cell(g, 0.0, 2.0), 100)

    def test_obstacle_in_lane_kept_and_strays_ignored(self):
        data = self.data.copy()
        data[int((0.3 - self.origin[1]) / self.res), int((1.0 - self.origin[0]) / self.res)] = O
        strays = np.vstack([self.cones, [[0.0, 2.6], [3.0, -2.5]]])   # duplicates/outliers off to the side
        g, _ = mc.drivable_grid(data, self.origin, self.res, self.path, strays)
        self.assertEqual(self.cell(g, 1.0, 0.3), 100)
        self.assertEqual(self.cell(g, 0.0, 0.0), 0)
        self.assertEqual(self.cell(g, 0.0, 2.0), 100)

    def test_needs_cones_on_both_sides(self):
        left_only = gate_cones(self.path)[: len(self.cones) // 2]
        g, why = mc.drivable_grid(self.data, self.origin, self.res, self.path, left_only)
        self.assertIsNone(g)
        self.assertIn('one side', why)


if __name__ == '__main__':
    unittest.main()
