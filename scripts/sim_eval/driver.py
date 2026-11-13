#!/usr/bin/env python3
"""Scripted joystick: drives one lap of the racetrack through the normal /joy interface.
Steering is closed-loop on simulator ground truth so both code versions drive the same path."""
import math, sys, time, os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from tf2_msgs.msg import TFMessage

SPEED = 1.0; LOOK = 0.9
def build_path():
    pts = [(-1.0, 0.0)]
    x = -1.0
    while x < 7.0: x += 0.1; pts.append((x, 0.0))
    for i in range(1, 41):
        a = -math.pi/2 + math.pi*i/40; pts.append((7.0 + 2*math.cos(a), 2.0 + 2*math.sin(a)))
    x = 7.0
    while x > -10.5: x -= 0.1; pts.append((x, 4.0))
    for i in range(1, 41):
        a = math.pi/2 + math.pi*i/40; pts.append((-10.5 + 2*math.cos(a), 2.0 + 2*math.sin(a)))
    x = -10.5
    while x < -2.0: x += 0.1; pts.append((x, 0.0))
    return pts

def bidirectional_path(forward, laps):
    """Keep one odometry/map session while turning around east of the racks."""
    path = forward * laps
    forward_end = len(path)
    # Continue east on the lower aisle, then make a 1 m radius U-turn in
    # the open area beyond the rack ends. All points remain physical motion.
    x = path[-1][0]
    while x < 10.0:
        x = min(10.0, x + 0.1)
        path.append((x, 0.0))
    for i in range(1, 41):
        angle = -math.pi/2 + math.pi*i/40
        path.append((10.0 + math.cos(angle), 1.0 + math.sin(angle)))
    # Smoothly join the westbound lower aisle with west-facing tangents.
    for i in range(1, 41):
        t = i/40
        x = (1-t)**3*10 + 3*(1-t)**2*t*9 + 3*(1-t)*t*t*8 + t**3*7
        y = (1-t)**3*2 + 3*(1-t)**2*t*2
        path.append((x, y))
    reverse = list(reversed(build_path()))
    start = min(range(len(reverse)), key=lambda i: math.hypot(reverse[i][0]-7, reverse[i][1]))
    reverse = reverse[start:] + reverse[:start]
    reverse_start = len(path)
    path += reverse * laps
    return path, forward_end, reverse_start

class Driver(Node):
    def __init__(self):
        super().__init__('scripted_joy')
        self.pub = self.create_publisher(Joy, '/joy', 10)
        self.create_subscription(TFMessage, '/gt_pose', self.gt_cb, 10)
        self.pose = None
    def gt_cb(self, msg):
        for index, t in enumerate(msg.transforms):
            if t.child_frame_id in ('rc_vehicle', 'rc_ackermann_vehicle') or (index == 0 and not t.child_frame_id):
                q = t.transform.rotation
                yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
                self.pose = (t.transform.translation.x, t.transform.translation.y, yaw)
    def send(self, throttle=0.0, steer=0.0, menu=0, view=0):
        m = Joy(); m.header.stamp = self.get_clock().now().to_msg()
        m.axes = [0.0]*8; m.axes[1] = float(throttle); m.axes[3] = float(steer)
        m.buttons = [0]*11; m.buttons[7] = menu; m.buttons[6] = view
        self.pub.publish(m)
    def hold(self, secs, **kw):
        t0 = time.time()
        while time.time() - t0 < secs:
            self.send(**kw); rclpy.spin_once(self, timeout_sec=0.05)
    def idle(self, secs):
        t0 = time.time()
        while time.time() - t0 < secs: rclpy.spin_once(self, timeout_sec=0.05)

def main():
    warmup = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
    rclpy.init(); d = Driver()
    t0 = time.time()
    while d.pose is None and time.time() - t0 < 60: rclpy.spin_once(d, timeout_sec=0.1)
    if d.pose is None: raise RuntimeError('DRIVER: no ground truth')
    print('DRIVER: ground truth ok, warming up'); sys.stdout.flush()
    d.hold(warmup)                       # neutral sticks while the estimator surveys
    d.hold(2.6, menu=1); d.hold(1.5)     # hold menu -> RUN_CONTROL (and wait for the RC state)
    print('DRIVER: driving'); sys.stdout.flush()
    laps = int(os.environ.get('LAPS', '1'))
    if laps < 1: raise ValueError('LAPS must be positive')
    path = build_path()
    if os.environ.get('REVERSE', '0') == '1': path = list(reversed(path))
    # Start at the nearest path point for alternative spawn locations.
    start = min(range(len(path)), key=lambda i: math.hypot(path[i][0]-d.pose[0], path[i][1]-d.pose[1]))
    path = path[start:]+path[:start]
    milestones = {}
    if os.environ.get('BIDIRECTIONAL', '0') == '1':
        if os.environ.get('REVERSE', '0') == '1':
            raise ValueError('BIDIRECTIONAL starts forward; do not set REVERSE')
        path, forward_end, reverse_start = bidirectional_path(path, laps)
        milestones = {forward_end: 'forward laps finished; turning around',
                      reverse_start: 'reverse laps started'}
    else:
        path = path*laps
    idx = 0; t0 = time.time()
    while time.time() - t0 < 600*laps:
        rclpy.spin_once(d, timeout_sec=0.05)
        x, y, yaw = d.pose
        # advance along the path to the first point beyond the lookahead distance
        while idx < len(path) - 1 and math.hypot(path[idx][0]-x, path[idx][1]-y) < LOOK: idx += 1
        for milestone in list(milestones):
            if idx >= milestone:
                print('DRIVER:', milestones.pop(milestone), flush=True)
        tx, ty = path[idx]
        if idx >= len(path) - 1 and math.hypot(tx-x, ty-y) < 0.5: break
        alpha = math.atan2(ty-y, tx-x) - yaw
        alpha = math.atan2(math.sin(alpha), math.cos(alpha))
        omega = 2.0*SPEED*math.sin(alpha)/LOOK
        d.send(throttle=SPEED, steer=max(-1.0, min(1.0, omega)))
    if idx < len(path)-1:
        d.hold(1.0)
        raise RuntimeError(f'DRIVER: lap timed out at {idx}/{len(path)}')
    print('DRIVER: lap done in %.1f s at idx %d/%d' % (time.time()-t0, idx, len(path))); sys.stdout.flush()
    d.hold(2.0)                          # stop
    d.hold(1.0, throttle=0.3)            # creep forward...
    print('DRIVER: joystick silent (controller-loss test)'); sys.stdout.flush()
    d.idle(4.0)                          # ...then the controller "disconnects"
    x1 = d.pose[0]; d.idle(2.0); print('DRIVER: moved %.2f m in 2 s after 4 s of silence' % abs(d.pose[0]-x1))
    d.hold(2.6, view=1); d.hold(1.0)     # hold view: FAULT -> STANDBY in the fixed code
    d.hold(2.6, menu=1); d.hold(1.0)     # original code: menu toggles RUN_CONTROL -> STANDBY
    print('DRIVER: finished'); sys.stdout.flush()

if __name__ == '__main__': main()
