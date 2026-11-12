#!/usr/bin/env python3
"""Record cone poses from Gazebo and report any cone that moves or tips over.

usage: cone_watch.py <world-name> <seconds> [output.json]
Run with the same GZ_PARTITION as the simulation (see a run's environment.txt).
"""
import json
import math
import sys
import time
from gz.transport13 import Node
from gz.msgs10.pose_v_pb2 import Pose_V

world, seconds = sys.argv[1], float(sys.argv[2])
out = sys.argv[3] if len(sys.argv) > 3 else None
first, last = {}, {}


def receive(msg):
    for p in msg.pose:
        if not p.name.startswith('cone_gate_'):
            continue
        q = p.orientation
        # Tilt of the cone's up axis from vertical.
        tilt = math.degrees(math.acos(max(-1.0, min(1.0, 1 - 2 * (q.x * q.x + q.y * q.y)))))
        rec = (p.position.x, p.position.y, p.position.z, tilt)
        first.setdefault(p.name, rec)
        last[p.name] = rec


node = Node()
if not node.subscribe(Pose_V, f'/world/{world}/pose/info', receive):
    sys.exit('cannot subscribe to Gazebo poses')
end = time.time() + seconds
while time.time() < end:
    time.sleep(0.2)
moved = {}
for name, (x0, y0, z0, _) in first.items():
    x1, y1, z1, tilt = last[name]
    shift = math.hypot(x1 - x0, y1 - y0)
    if shift > 0.01 or tilt > 10 or abs(z1 - z0) > 0.005:
        moved[name] = {'moved_m': round(shift, 3), 'tilt_deg': round(tilt, 1), 'z_m': round(z1, 4)}
report = {'cones_seen': len(first), 'disturbed': moved,
          'max_settled_z_m': round(max((v[2] for v in last.values()), default=0.0), 4)}
print(json.dumps(report, indent=1))
if out:
    json.dump(report, open(out, 'w'), indent=1)
