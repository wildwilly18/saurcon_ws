#!/usr/bin/env python3
"""Drive with a cone-vision policy in ROS 2: camera in, /auto_cmd out. No map, no localization.

Pipeline (the same as saurcon_rl.cone_drive in MuJoCo):
  /oak/rgb/image_raw + /oak/stereo/image_raw (aligned depth)
    -> cones.ConeDetector -> cone base points in the camera optical frame
    -> TF base_link <- camera -> (x, y) in base_link
    -> cone_env.encode(...) with speed and yaw rate from the odometry UKF (/saurcon/odom_nav)
    -> policy -> /auto_cmd (used by the state machine in RUN_AUTONOMOUS)

The policy runs at 20 Hz like training. Each colour image is used as soon as it
arrives, with the most recent depth image if it is within `depth_max_age`
(otherwise cone size gives the range). Detections go into a short cone memory
(cone_env.ConeMemory, ~2 s) in the odom frame and are re-expressed in the
current base_link at every control step, exactly as in training: the policy
sees cones where they are now, including ones that have left the camera's view. If no image has arrived for `image_timeout` seconds it stops.
Detector colour thresholds are parameters (defaults are tuned for the Gazebo cones).

Run with the RL virtual environment's Python (it needs torch):
  .venv-rl/bin/python -m saurcon_rl.cone_policy_node --ros-args -p model:=<model.zip>
"""
import math
from pathlib import Path

import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import Buffer, TransformException, TransformListener

from saurcon_rl.cone_env import ConeMemory, encode
from saurcon_rl.cone_mapper_node import tf_matrix
from saurcon_rl.cones import ConeDetector
from saurcon_rl.env import CTRL_DT, STEER_MAX, V_MAX, WHEELBASE


class ConePolicyNode(Node):
    def __init__(self):
        super().__init__('cone_policy')
        from stable_baselines3 import PPO
        model = self.declare_parameter('model', '').value
        if not model or not Path(model).exists():
            raise FileNotFoundError(f'model parameter must point to a trained cone policy (got "{model}")')
        self.policy = PPO.load(model, device='cpu')
        self.speed_limit = self.declare_parameter('speed_limit', V_MAX).value
        self.image_timeout = self.declare_parameter('image_timeout', 0.3).value
        self.hsv_lo = tuple(self.declare_parameter('hsv_lo', [15, 150, 110]).value)
        self.hsv_hi = tuple(self.declare_parameter('hsv_hi', [32, 255, 255]).value)
        self.camera_height = self.declare_parameter('camera_height', 0.137).value
        self.camera_frame = self.declare_parameter('camera_frame', 'oak_rgb_camera_optical_frame').value
        self.detector, self.cones = None, np.zeros((0, 2))
        self.last_image = None
        self.v = self.yaw_rate = 0.0
        self.steer_est = 0.0
        self.prev_action = np.array([-1.0, 0.0], np.float32)
        self.bridge = CvBridge()
        self.tf = Buffer(); self.tf_listener = TransformListener(self.tf, self)
        self.create_subscription(CameraInfo, '/oak/rgb/camera_info', self.on_info, 10)
        self.create_subscription(Odometry, '/saurcon/odom_nav', self.on_odom, 10)
        self.depth_max_age = self.declare_parameter('depth_max_age', 0.1).value
        self.depth_msg = None
        self.memory = ConeMemory()
        self.create_subscription(Image, '/oak/rgb/image_raw', self.on_rgb, qos_profile_sensor_data)
        self.create_subscription(Image, '/oak/stereo/image_raw', self.on_depth, qos_profile_sensor_data)
        self.pub = self.create_publisher(Twist, '/auto_cmd', 10)
        self.create_timer(CTRL_DT, self.step)
        self.stats = {'images': 0, 'dets': 0, 'stale_steps': 0, 'rgb': 0, 'depth': 0, 'size_ranged': 0, 'ground_ranged': 0}
        self.create_timer(5.0, self.report)
        self.get_logger().info(f'cone policy {model}, speed limit {self.speed_limit} m/s')

    def count(self, key):
        self.stats[key] += 1

    def report(self):
        s = self.stats
        self.get_logger().info(f"last 5 s (sim): rgb {s['rgb']}, depth {s['depth']}, used {s['images']}, "
                               f"detections/image {s['dets'] / max(s['images'], 1):.1f} (depth {s['dets'] - s['size_ranged'] - s['ground_ranged']}, ground {s['ground_ranged']}, size {s['size_ranged']}), "
                               f"stale control steps {s['stale_steps']}/100")
        self.stats = dict.fromkeys(s, 0)

    def on_info(self, msg):
        if self.detector is None:
            K = msg.k
            self.detector = ConeDetector(K[0], K[4], K[2], K[5], hsv_lo=self.hsv_lo, hsv_hi=self.hsv_hi,
                                         camera_height=self.camera_height)

    def on_odom(self, msg):
        self.v = msg.twist.twist.linear.x
        self.yaw_rate = msg.twist.twist.angular.z

    def on_depth(self, msg):
        self.depth_msg = msg
        self.stats['depth'] += 1

    @staticmethod
    def stamp_s(msg):
        return msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

    def on_rgb(self, rgb_msg):
        self.stats['rgb'] += 1
        if self.detector is None:
            return
        try:
            cam = self.tf.lookup_transform('base_link', self.camera_frame, Time())
            odom_base = self.tf.lookup_transform('odom', 'base_link', rgb_msg.header.stamp)
        except TransformException:
            try:   # image newer than the latest odometry: use the latest
                odom_base = self.tf.lookup_transform('odom', 'base_link', Time())
            except TransformException:
                return
        depth = None
        if self.depth_msg is not None and abs(self.stamp_s(self.depth_msg) - self.stamp_s(rgb_msg)) <= self.depth_max_age:
            depth = self.bridge.imgmsg_to_cv2(self.depth_msg).astype(np.float32)
            if self.depth_msg.encoding == '16UC1':
                depth /= 1000.0
        dets = self.detector.detect(self.bridge.imgmsg_to_cv2(rgb_msg, 'bgr8'), depth)
        R, p = tf_matrix(cam)
        base = np.array([(R @ d.p_cam + p)[:2] for d in dets]).reshape(-1, 2)
        Ro, po = tf_matrix(odom_base)
        self.memory.update(base @ Ro[:2, :2].T + po[:2], self.get_clock().now().nanoseconds * 1e-9)   # odom frame
        self.last_image = self.get_clock().now()
        self.stats['images'] += 1; self.stats['dets'] += len(dets)
        self.stats['size_ranged'] += sum(d.method == 'size' for d in dets)
        self.stats['ground_ranged'] += sum(d.method == 'ground' for d in dets)

    def step(self):
        cmd = Twist()
        fresh = (self.last_image is not None and
                 (self.get_clock().now() - self.last_image).nanoseconds * 1e-9 < self.image_timeout)
        if fresh:
            try:
                Ro, po = tf_matrix(self.tf.lookup_transform('odom', 'base_link', Time()))
            except TransformException:
                Ro, po = np.eye(3), np.zeros(3)
            yaw = math.atan2(Ro[1, 0], Ro[0, 0])
            rel, ages = self.memory.relative(po[0], po[1], yaw, self.get_clock().now().nanoseconds * 1e-9)
            obs = encode(rel, self.v, self.yaw_rate, self.steer_est, self.prev_action, ages)
            action, _ = self.policy.predict(obs, deterministic=True)
            action = np.clip(action, -1, 1).astype(np.float32)
            v_cmd = min((float(action[0]) + 1) / 2 * V_MAX, self.speed_limit)
            steer_cmd = float(action[1]) * STEER_MAX
            self.steer_est += (steer_cmd - self.steer_est) * min(1.0, CTRL_DT / 0.2)
            self.prev_action = action
            cmd.linear.x = v_cmd
            # Gazebo's AckermannSteering plugin takes a yaw rate and turns it into a steering
            # angle with its own ramped speed, not the commanded one. Use the measured speed
            # (which tracks the ramp) so the plugin's angle equals the policy's; with the
            # commanded speed it steers harder while accelerating and softer while braking.
            cmd.angular.z = max(self.v, 0.0) * math.tan(steer_cmd) / WHEELBASE
        else:
            self.stats['stale_steps'] += 1
            self.get_logger().warn('no camera images; stopping', throttle_duration_sec=2.0)
        if rclpy.ok():
            self.pub.publish(cmd)


def main():
    rclpy.init()
    node = ConePolicyNode()
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
