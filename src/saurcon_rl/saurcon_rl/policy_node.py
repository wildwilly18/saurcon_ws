#!/usr/bin/env python3
"""Drive the car with a trained racing policy.

Reads the fused state estimate (/saurcon/nav_state, map frame), builds the same
observation as the training environment, and publishes /auto_cmd for the state
machine (used in RUN_AUTONOMOUS). Runs at 20 Hz like training.

The track is defined in the Gazebo world frame; `map_origin` is the world pose
of the map frame's origin (the rear axle where mapping started). For the
racetrack's spawn pose that is (-1.127, 0, 0).

Stale input stops the car. A state counts only while its header stamp is within
`state_timeout` (s) of the node's clock; states that are older, not newer than the last
accepted one, or not finite are dropped. Without a valid state the node publishes a zero
command every step (so the RC watchdog still sees a live, deliberate stop) and resets
its command history, so recovery does not reuse an obsolete action.

Run with the RL virtual environment's Python (it needs torch):
  .venv-rl/bin/python -m saurcon_rl.policy_node --ros-args -p model:=<model.zip> ...
"""
import math
from pathlib import Path

import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from saurcon_rl.env import CTRL_DT, STEER_MAX, V_MAX, WHEELBASE, default_worlds, observe
from saurcon_rl.track import Track


class PolicyNode(Node):
    def __init__(self):
        super().__init__('race_policy')
        from stable_baselines3 import PPO
        model = self.declare_parameter('model', '').value
        world = self.declare_parameter('world', str(default_worlds() / 'racetrack.world')).value
        reverse = self.declare_parameter('reverse', False).value
        ox, oy, oyaw = self.declare_parameter('map_origin', [-1.127, 0.0, 0.0]).value
        self.speed_limit = self.declare_parameter('speed_limit', V_MAX).value
        self.state_timeout = float(self.declare_parameter('state_timeout', 0.25).value)
        if not model or not Path(model).exists():
            raise FileNotFoundError(f'model parameter must point to a trained policy (got "{model}")')
        self.policy = PPO.load(model, device='cpu')
        self.track = Track.from_world(world, reverse=reverse)
        self.origin = (ox, oy, oyaw)
        self.state, self.state_stamp, self.i = None, None, None
        self.reset_history()
        self.create_subscription(Odometry, '/saurcon/nav_state', self.on_state, 10)
        self.pub = self.create_publisher(Twist, '/auto_cmd', 10)
        self.create_timer(CTRL_DT, self.step)
        self.get_logger().info(f'Policy {model} on {self.track.name} '
                               f'({self.track.length:.1f} m), speed limit {self.speed_limit} m/s')

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def warn(self, text):
        self.get_logger().warn(text, throttle_duration_sec=2.0)

    def reset_history(self):
        self.prev_action = np.array([-1.0, 0.0], np.float32)
        self.steer_est = 0.0

    def on_state(self, msg):
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if self.state_stamp is not None and self.now_s() < self.state_stamp:
            self.state_stamp = None                 # clock went backwards (simulation reset)
        if stamp <= 0.0 or (self.state_stamp is not None and stamp <= self.state_stamp):
            return                              # unstamped, or not newer than what we have
        if self.now_s() - stamp > self.state_timeout:
            return                              # already expired on arrival
        p = msg.pose.pose
        yaw = math.atan2(2 * (p.orientation.w * p.orientation.z + p.orientation.x * p.orientation.y),
                         1 - 2 * (p.orientation.y ** 2 + p.orientation.z ** 2))
        ox, oy, oyaw = self.origin
        c, s = math.cos(oyaw), math.sin(oyaw)
        x = ox + c * p.position.x - s * p.position.y
        y = oy + s * p.position.x + c * p.position.y
        state = (x, y, yaw + oyaw, msg.twist.twist.linear.x, msg.twist.twist.angular.z)
        if not all(math.isfinite(v) for v in state):
            return
        self.state, self.state_stamp = state, stamp

    def state_fresh(self):
        return self.state is not None and self.now_s() - self.state_stamp <= self.state_timeout

    def step(self):
        if not self.state_fresh():
            # no navigation state, or it stopped updating: stop, and forget the command history
            if self.state is not None:
                self.warn(f'navigation state older than {self.state_timeout} s; stopping')
            self.state, self.i = None, None
            self.reset_history()
            self.pub.publish(Twist())
            return
        x, y, yaw, v, yaw_rate = self.state
        self.i = self.track.project(x, y, hint=self.i)
        # Actual steering is not measured; model it like the training environment
        # (first-order lag of the commanded angle).
        obs = observe(self.track, self.i, x, y, yaw, v, yaw_rate, self.steer_est, self.prev_action)
        action, _ = self.policy.predict(obs, deterministic=True)
        action = np.clip(action, -1, 1).astype(np.float32)
        v_cmd = min((float(action[0]) + 1) / 2 * V_MAX, self.speed_limit)
        steer_cmd = float(action[1]) * STEER_MAX
        self.steer_est += (steer_cmd - self.steer_est) * min(1.0, CTRL_DT / 0.2)
        self.prev_action = action
        cmd = Twist()
        cmd.linear.x = v_cmd
        # Gazebo's AckermannSteering plugin takes a yaw rate and turns it into a steering
        # angle with its own ramped speed, not the commanded one. Use the measured speed
        # (which tracks the ramp) so the plugin's angle equals the policy's; with the
        # commanded speed it steers harder while accelerating and softer while braking.
        cmd.angular.z = max(v, 0.0) * math.tan(steer_cmd) / WHEELBASE
        self.pub.publish(cmd)


def main():
    rclpy.init()
    node = PolicyNode()
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
