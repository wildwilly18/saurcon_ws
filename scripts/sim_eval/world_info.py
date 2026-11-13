"""World facts the evaluation tools need, read from the world file instead of hard-coded.

name: the <world name="..."> (Gazebo topics are /world/<name>/...).
spawn: the rc_vehicle include's pose (model origin x, y, yaw) - the start line and, for a
       map started at the spawn, the origin of RTAB-Map's map frame.
The world used by a run: SIM_WORLD (set by runsim.sh from the world:= launch argument),
else the default racetrack.
"""
import math
import os
import re
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
DEFAULT_WORLD = WS / 'src/middle_earth/worlds/racetrack.world'
REAR_AXLE_BACK = 0.127          # base_link (rear axle) behind the model origin
VEHICLE = re.compile(r'<include>\s*<uri>model://rc_ackermann_vehicle</uri>\s*<name>([^<]+)</name>\s*<pose>([^<]+)</pose>')


def run_world():
    return Path(os.environ.get('SIM_WORLD') or DEFAULT_WORLD)


def world_name(path=None):
    text = Path(path or run_world()).read_text()
    return re.search(r'<world name="([^"]+)"', text).group(1)


def spawn(path=None):
    """(x, y, yaw) of the vehicle's model origin at spawn."""
    m = VEHICLE.search(Path(path or run_world()).read_text())
    if not m:
        return (-1.0, 0.0, 0.0)
    v = [float(t) for t in m.group(2).split()]
    return (v[0], v[1], v[5] if len(v) > 5 else 0.0)


def start_line(path=None, ahead=0.5):
    """Start/finish line pose: `ahead` m in front of the spawn, so a car settling at the spawn
    cannot jitter across it before it drives."""
    x, y, yaw = spawn(path)
    return (x + ahead * math.cos(yaw), y + ahead * math.sin(yaw), yaw)


def map_origin(path=None):
    """World pose (x, y, yaw) of an RTAB-Map frame started at the spawn: the rear axle there."""
    x, y, yaw = spawn(path)
    return (x - REAR_AXLE_BACK * math.cos(yaw), y - REAR_AXLE_BACK * math.sin(yaw), yaw)


def crossed(start, p0, p1, half_width=1.5):
    """True if the move p0 -> p1 crosses the start line forwards: the line through `start`
    (x, y, yaw) square to its heading, within half_width of it."""
    sx, sy, yaw = start
    c, s = math.cos(yaw), math.sin(yaw)
    a0 = (p0[0] - sx) * c + (p0[1] - sy) * s          # along the start heading
    a1 = (p1[0] - sx) * c + (p1[1] - sy) * s
    lat = -(p1[0] - sx) * s + (p1[1] - sy) * c
    return abs(lat) < half_width and a0 < 0.0 <= a1


def to_frame(xy, origin):
    """World points (N, 2) expressed in the frame whose world pose is origin (x, y, yaw)."""
    import numpy as np
    ox, oy, yaw = origin
    c, s = math.cos(yaw), math.sin(yaw)
    d = np.asarray(xy, float).reshape(-1, 2) - (ox, oy)
    return np.column_stack([c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1]])


def world_from_launch_log(log):
    """The world file named in a run's launch.log (for runs recorded before SIM_WORLD)."""
    found = re.search(r'(?<![\w\]])(/[^\s:\[\]@"]+\.world)', Path(log).read_text(errors='ignore'))
    return Path(found.group(1)) if found else DEFAULT_WORLD
