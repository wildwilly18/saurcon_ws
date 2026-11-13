"""make_race_video.py on runs with and without SLAM maps (review finding 6).

Run:  PYTHONPATH=src/saurcon_plan:$PYTHONPATH .venv-rl/bin/python -m pytest -q scripts/sim_eval/tests
"""
import csv
import importlib.util
from pathlib import Path

import cv2
import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('make_race_video', HERE / 'make_race_video.py')
mrv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mrv)

TRUE_CONES = np.array([[0.0, 1.1], [0.0, -1.1], [2.0, 1.1], [2.0, -1.1]])


def make_run(tmp, *, chase=True, map_rows=False, grid=False, index='none', n=12):
    """A tiny synthetic run: the car drives 1 m/s along x for n frames at 10 Hz."""
    run = tmp / 'run'
    (run / 'frames').mkdir(parents=True)
    with open(run / 'log.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t', 'kind', 'a', 'b', 'c'])
        for k in range(n):
            t = 10 + 0.1 * k
            w.writerow([t, 'gt', -3 + 0.1 * k, 0.0, 0.0])
            w.writerow([t, 'frame', k, '', ''])
            if map_rows:
                w.writerow([t, 'map', -2 + 0.1 * k, 0.0, 0.0])
            cv2.imwrite(str(run / 'frames' / f'{k:06d}.jpg'), np.full((400, 640, 3), 90, np.uint8))
    if chase:
        (run / 'chase').mkdir()
        with open(run / 'chase' / 'stamps.csv', 'w') as f:
            f.write('t,frame\n')
            for k in range(n):
                f.write(f'{10 + 0.1 * k},{k}\n')
                cv2.imwrite(str(run / 'chase' / f'{k:06d}.jpg'), np.full((400, 640, 3), 150, np.uint8))
    (run / 'launch.log').write_text('no world here\n')
    if index != 'none':
        (run / 'maps').mkdir()
        with open(run / 'maps' / 'index.csv', 'w') as f:
            f.write('frame,stamp,origin_x,origin_y,resolution,width,height\n')
            if index == 'rows':
                f.write('0,9.0,-5.0,-3.0,0.05,200,120\n')
        if grid:
            g = np.full((120, 200), 127, np.uint8); g[40:80, 50:150] = 255; g[60, 60:140] = 0
            cv2.imwrite(str(run / 'maps' / '0000.png'), g)
    return run


def frames_of(path):
    cap = cv2.VideoCapture(str(path))
    shapes = []
    while True:
        ok, img = cap.read()
        if not ok:
            break
        shapes.append(img.shape)
    return shapes


def test_non_slam_run_has_no_map_panel(tmp_path):
    run = make_run(tmp_path)
    mrv.main([str(run), str(tmp_path / 'v.mp4')])
    shapes = frames_of(tmp_path / 'v.mp4')
    assert shapes and all(s[:2] == (400, 1280) for s in shapes)


def test_header_only_index_is_ignored(tmp_path):
    run = make_run(tmp_path, index='header')
    assert mrv.map_records(run) == []
    mrv.main([str(run), str(tmp_path / 'v.mp4')])
    assert all(s[:2] == (400, 1280) for s in frames_of(tmp_path / 'v.mp4'))


def test_index_row_without_image_is_ignored(tmp_path):
    run = make_run(tmp_path, index='rows', grid=False)
    assert mrv.map_records(run) == []


def test_grid_without_map_trajectory_renders(tmp_path):
    run = make_run(tmp_path, index='rows', grid=True, map_rows=False)
    panel = mrv.MapPanel(run, TRUE_CONES)
    assert panel.path.shape == (0, 4)
    img = panel.render(10.5)
    assert img.shape == (panel.h, mrv.PANEL_W, 3)
    mrv.main([str(run), str(tmp_path / 'v.mp4')])
    assert all(s[0] > 400 for s in frames_of(tmp_path / 'v.mp4'))     # panel stacked below


def test_full_slam_run_renders_panel_with_path(tmp_path):
    run = make_run(tmp_path, index='rows', grid=True, map_rows=True)
    (run / 'cones_rtab.csv').write_text('9.5;0.0 1.1;0.0 -1.1\n\n')
    panel = mrv.MapPanel(run, TRUE_CONES)
    assert panel.path.shape == (12, 4) and len(panel.cones) == 1
    empty = mrv.MapPanel(run, TRUE_CONES).render(8.0)        # before the first grid: all unknown
    drawn = panel.render(11.0)
    assert (drawn != empty).any()


def test_without_chase_camera_onboard_only(tmp_path):
    run = make_run(tmp_path, chase=False)
    mrv.main([str(run), str(tmp_path / 'v.mp4')])
    shapes = frames_of(tmp_path / 'v.mp4')
    assert shapes and all(s[:2] == (400, 640) for s in shapes)


@pytest.mark.skipif(not (HERE.parents[1] / 'evaluation/cones_gz/classical_slam_rt2/maps/index.csv').exists(),
                    reason='recorded SLAM run not present')
def test_recorded_slam_run_panel():
    run = HERE.parents[1] / 'evaluation/cones_gz/classical_slam_rt2'
    panel = mrv.MapPanel(run, TRUE_CONES)
    assert len(panel.maps) > 10 and len(panel.path) > 100
    assert panel.render(panel.maps[-1][0]).shape == (panel.h, mrv.PANEL_W, 3)


def test_follower_waypoints_on_track_view_without_slam(tmp_path):
    """Classical follower log, no SLAM: a ground-truth track panel with the waypoints placed by the car pose."""
    run = make_run(tmp_path)
    with open(run / 'follower.csv', 'w') as f:
        for k in range(12):
            f.write(f"{10 + 0.1 * k:.3f};0;0;0;1;0;0;0.1;0.0;(1.0, 0.0);[[0.0, 0.0], [1.0, 0.0], [2.0, 0.5]];[]\n")
        f.write('garbage line\n')
    panel = mrv.MapPanel(run, TRUE_CONES, [])
    assert not panel.slam and len(panel.waypoints) == 12
    t, pts, target = panel.waypoints[0]
    # car at world (-3, 0), yaw 0 -> rear axle -3.127 -> map frame -2.0; first waypoint is the rear axle
    assert pts[0] == pytest.approx((-3 - mrv.REAR_AXLE_BACK - mrv.MAP_ORIGIN[0], 0.0))
    assert target == pytest.approx(pts[0] + (1.0, 0.0))
    mrv.main([str(run), str(tmp_path / 'v.mp4')])
    assert all(s[0] > 400 for s in frames_of(tmp_path / 'v.mp4'))


def test_map_from_puts_occupancy_behind_non_slam_run(tmp_path):
    slam = make_run(tmp_path / 'slam', index='rows', grid=True, map_rows=True)
    run = make_run(tmp_path / 'plain')
    (run / 'follower.csv').write_text('10.0;0;0;0;1;0;0;0.1;0.0;(1.0, 0.0);[[0.0, 0.0], [1.0, 0.0]];[]\n')
    plain = mrv.MapPanel(run, TRUE_CONES, []).render(10.0)
    panel = mrv.MapPanel(run, TRUE_CONES, [], background=slam)
    assert panel.background and not panel.slam
    assert (panel.render(10.0) != plain).any()                  # the grid is drawn from the first frame
    mrv.main([str(run), str(tmp_path / 'v.mp4'), '--map-from', str(slam)])
    assert all(s[0] > 400 for s in frames_of(tmp_path / 'v.mp4'))
