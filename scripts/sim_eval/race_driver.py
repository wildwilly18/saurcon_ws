#!/usr/bin/env python3
"""Hand the car to the autonomous policy for a number of laps, then take it back.

Plays the role of the person holding the controller: waits for the estimator,
holds view for 2 s (STANDBY -> RUN_AUTONOMOUS), keeps the joystick heartbeat
alive (the dead-man switch), counts laps from ground truth at the start line,
then holds menu (RUN_AUTONOMOUS -> STANDBY).

usage: race_driver.py [warmup_s]   env: RACE_LAPS (default 3), RACE_TIMEOUT (s, default 240)
"""
import math
import os
import sys
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from tf2_msgs.msg import TFMessage

START_X = -1.0          # model-origin x of the start line (spawn pose), on the y=0 straight


class RaceDriver(Node):
    def __init__(self):
        super().__init__('race_driver')
        self.pub = self.create_publisher(Joy, '/joy', 10)
        self.create_subscription(TFMessage, '/gt_pose', self.gt, 10)
        self.pose, self.laps, self.lap_t, self.prev = None, 0, [], None

    def gt(self, msg):
        t = msg.transforms[0]
        x, y = t.transform.translation.x, t.transform.translation.y
        stamp = t.header.stamp.sec + t.header.stamp.nanosec * 1e-9
        if self.prev is not None:
            px, py = self.prev
            # Crossing the start line forwards on the bottom straight.
            if abs(y) < 1.5 and px < START_X <= x:
                self.lap_t.append(stamp)
                if len(self.lap_t) > 1:
                    self.laps += 1
                    print(f'RACE: lap {self.laps} {self.lap_t[-1] - self.lap_t[-2]:.2f} s', flush=True)
        self.prev, self.pose = (x, y), (x, y, stamp)

    def send(self, menu=0, view=0):
        m = Joy(); m.header.stamp = self.get_clock().now().to_msg()
        m.axes = [0.0] * 8; m.buttons = [0] * 11; m.buttons[7] = menu; m.buttons[6] = view
        self.pub.publish(m)

    def hold(self, secs, **kw):
        t0 = time.time()
        while time.time() - t0 < secs:
            self.send(**kw); rclpy.spin_once(self, timeout_sec=0.05)


def main():
    warmup = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0
    laps = int(os.environ.get('RACE_LAPS', '3'))
    timeout = float(os.environ.get('RACE_TIMEOUT', '240'))
    rclpy.init(); d = RaceDriver()
    t0 = time.time()
    while d.pose is None and time.time() - t0 < 60:
        rclpy.spin_once(d, timeout_sec=0.1)
    if d.pose is None:
        raise RuntimeError('RACE: no ground truth')
    print('RACE: ground truth ok, warming up', flush=True)
    d.hold(warmup)
    d.hold(2.6, view=1); d.hold(0.5)
    print('RACE: autonomous', flush=True)
    t0 = time.time(); start = d.pose
    while d.laps < laps and time.time() - t0 < timeout:
        d.hold(0.2)
    d.hold(2.6, menu=1); d.hold(1.0)
    times = [b - a for a, b in zip(d.lap_t, d.lap_t[1:])]
    print(f'RACE: finished {d.laps} laps; lap times {[round(t, 2) for t in times]}; '
          f'first line crossing {d.lap_t[0] - start[2]:.2f} s after start' if d.lap_t else
          f'RACE: no start-line crossing in {timeout} s', flush=True)


if __name__ == '__main__':
    main()
