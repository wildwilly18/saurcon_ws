#!/usr/bin/env python3
"""Drive the car with a trained racing policy.

Reads the fused state estimate (/saurcon/nav_state, map frame), builds the same
observation as the training environment, and publishes /auto_cmd for the state
machine (used in RUN_AUTONOMOUS). Runs at 20 Hz like training.

The track is defined in the Gazebo world frame; `map_origin` is the world pose
of the map frame's origin (the rear axle where mapping started). For the
racetrack's spawn pose that is (-1.127, 0, 0).

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
        if not model or not Path(model).exists():
            raise FileNotFoundError(f'model parameter must point to a trained policy (got "{model}")')
        self.policy = PPO.load(model, device='cpu')
        self.track = Track.from_world(world, reverse=reverse)
        self.origin = (ox, oy, oyaw)
        self.state, self.i = None, None
        self.prev_action = np.array([-1.0, 0.0], np.float32)
        self.steer_est = 0.0
        self.create_subscription(Odometry, '/saurcon/nav_state', self.on_state, 10)
        self.pub = self.create_publisher(Twist, '/auto_cmd', 10)
        self.create_timer(CTRL_DT, self.step)
        self.get_logger().info(f'Policy {model} on {self.track.name} '
                               f'({self.track.length:.1f} m), speed limit {self.speed_limit} m/s')

    def on_state(self, msg):
        p = msg.pose.pose
        yaw = math.atan2(2 * (p.orientation.w * p.orientation.z + p.orientation.x * p.orientation.y),
                         1 - 2 * (p.orientation.y ** 2 + p.orientation.z ** 2))
        ox, oy, oyaw = self.origin
        c, s = math.cos(oyaw), math.sin(oyaw)
        x = ox + c * p.position.x - s * p.position.y
        y = oy + s * p.position.x + c * p.position.y
        self.state = (x, y, yaw + oyaw, msg.twist.twist.linear.x, msg.twist.twist.angular.z)

    def step(self):
        if self.state is None:
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
