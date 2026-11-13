#!/usr/bin/env python3
"""Drive with the classical cone follower in ROS 2: camera in, /auto_cmd out. No map, no localization.

Pipeline (the same as saurcon_rl.cone_drive runs in MuJoCo):
  /oak/rgb/image_raw + /oak/stereo/image_raw (aligned depth)
    -> cones.ConeDetector -> cone base points in the camera optical frame
    -> TF base_link <- camera -> (x, y) in base_link
    -> memory.ConeMemory in the odom frame (odometry UKF: TF odom -> base_link, /saurcon/odom_nav)
    -> cone_follower.ConeFollower: centreline from the cone gates, pure pursuit, curvature
       speed profile -> /auto_cmd (used by the state machine in RUN_AUTONOMOUS)

The follower runs at 20 Hz. Each colour image is used as soon as it and its own depth image
(same stamp) have arrived, with the odometry pose at the image's stamp (otherwise cone size
gives the range). Detections go into the cone memory (`memory_s`, default the follower's 5 s)
in the odom frame and are re-expressed in the current base_link at every control step, so the
follower sees cones where they are now, including ones that have left the camera's view. Its
`latency` parameter (s) predicts the pose ahead before steering.

Stale input stops the car (zero /auto_cmd every step, command history reset):
  - no image captured within `image_timeout` s (judged by the image stamp, not by when it was processed);
  - no odometry message stamped within `odom_timeout` s (speed and yaw rate come from it);
  - no odom -> base_link transform, or the latest one older than `tf_timeout` s. The pose is
    extrapolated over normal lag, never over an arbitrarily old transform. A missing or expired
    transform also clears the cone memory, whose odom-frame positions can no longer be trusted.
An image whose own pose never arrives is used with the latest pose only if that pose is within
`tf_fallback_max` s of the image stamp; otherwise it is dropped.
Detector colour thresholds are parameters (defaults are tuned for the Gazebo cones).

  ros2 run saurcon_plan cone_follower --ros-args -p use_sim_time:=true
(or launch full_sim_saurcon.launch.py cone_follower:=true)
"""
import math

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

from saurcon_plan.cone_follower import ConeFollower
from saurcon_plan.cone_mapper_node import tf_matrix
from saurcon_plan.cones import ConeDetector
from saurcon_plan.memory import ConeMemory
from saurcon_plan.vehicle import CTRL_DT, STEER_MAX, V_MAX, WHEELBASE, slew_steer


class ConeFollowerNode(Node):
    def __init__(self):
        super().__init__('cone_follower')
        self.follower = ConeFollower(latency=self.declare_parameter('latency', 0.05).value)
        dbg = self.declare_parameter('debug_csv', '').value      # per-step follower state, for debugging
        self.debug = open(dbg, 'w') if dbg else None
        self.speed_limit = self.declare_parameter('speed_limit', V_MAX).value
        self.image_timeout = self.declare_parameter('image_timeout', 0.3).value
        self.hsv_lo = tuple(self.declare_parameter('hsv_lo', [15, 150, 110]).value)
        self.hsv_hi = tuple(self.declare_parameter('hsv_hi', [32, 255, 255]).value)
        self.camera_height = self.declare_parameter('camera_height', 0.137).value
        self.camera_frame = self.declare_parameter('camera_frame', 'oak_rgb_camera_optical_frame').value
        self.detector, self.cones = None, np.zeros((0, 2))
        self.last_image = None          # capture stamp (s) of the newest image used
        self.v = self.yaw_rate = 0.0
        self.odom_stamp = None
        self.odom_timeout = float(self.declare_parameter('odom_timeout', 0.25).value)
        self.tf_timeout = float(self.declare_parameter('tf_timeout', 0.25).value)
        self.tf_fallback_max = float(self.declare_parameter('tf_fallback_max', 0.1).value)
        self.prev_action = np.array([-1.0, 0.0], np.float32)
        self.bridge = CvBridge()
        self.tf = Buffer(); self.tf_listener = TransformListener(self.tf, self)
        self.create_subscription(CameraInfo, '/oak/rgb/camera_info', self.on_info, 10)
        self.create_subscription(Odometry, '/saurcon/odom_nav', self.on_odom, 10)
        self.depth_max_age = self.declare_parameter('depth_max_age', 0.005).value   # s: same frame only
        self.depths, self.pending = [], []
        self.tf_wait = self.declare_parameter('tf_wait', 0.25).value   # s an image may wait for its pose
        # how long a cone is remembered after its last sighting (see ConeFollower.memory_s)
        self.memory_s = float(self.declare_parameter('memory_s', self.follower.memory_s).value)
        self.memory = ConeMemory(horizon=self.memory_s)
        self.create_subscription(Image, '/oak/rgb/image_raw', self.on_rgb, qos_profile_sensor_data)
        self.create_subscription(Image, '/oak/stereo/image_raw', self.on_depth, qos_profile_sensor_data)
        self.pub = self.create_publisher(Twist, '/auto_cmd', 10)
        self.create_timer(CTRL_DT, self.step)
        self.stats = {'images': 0, 'dets': 0, 'stale_steps': 0, 'rgb': 0, 'depth': 0, 'size_ranged': 0, 'ground_ranged': 0, 'tf_fallback': 0, 'tf_dropped': 0, 'tf_lag_ms': 0, 'no_depth': 0}
        self.create_timer(5.0, self.report)
        self.get_logger().info(f'classical cone follower, speed limit {self.speed_limit} m/s')

    def count(self, key):
        self.stats[key] += 1

    def report(self):
        s = self.stats
        self.get_logger().info(f"last 5 s (sim): rgb {s['rgb']}, depth {s['depth']}, used {s['images']}, "
                               f"detections/image {s['dets'] / max(s['images'], 1):.1f} (depth {s['dets'] - s['size_ranged'] - s['ground_ranged']}, ground {s['ground_ranged']}, size {s['size_ranged']}), "
                               f"stale control steps {s['stale_steps']}/100, images without their own pose {s['tf_fallback']} (dropped {s['tf_dropped']}), max odometry lag {s['tf_lag_ms']} ms, images without their depth {s['no_depth']}")
        self.stats = dict.fromkeys(s, 0)

    def on_info(self, msg):
        if self.detector is None:
            K = msg.k
            self.detector = ConeDetector(K[0], K[4], K[2], K[5], hsv_lo=self.hsv_lo, hsv_hi=self.hsv_hi,
                                         camera_height=self.camera_height)

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def warn(self, text):
        self.get_logger().warn(text, throttle_duration_sec=2.0)

    def on_odom(self, msg):
        stamp = self.stamp_s(msg)
        if self.odom_stamp is not None and self.now_s() < self.odom_stamp:
            self.odom_stamp = None                  # clock went backwards (simulation reset)
        v, r = msg.twist.twist.linear.x, msg.twist.twist.angular.z
        if stamp <= 0.0 or (self.odom_stamp is not None and stamp <= self.odom_stamp) \
                or not (math.isfinite(v) and math.isfinite(r)):
            return                                  # unstamped, not newer, or invalid
        self.v, self.yaw_rate, self.odom_stamp = v, r, stamp

    def on_depth(self, msg):
        self.depths.append(msg); del self.depths[:-6]
        self.stats['depth'] += 1

    @staticmethod
    def stamp_s(msg):
        return msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

    def on_rgb(self, rgb_msg):
        self.stats['rgb'] += 1
        if self.detector is None:
            return
        self.pending.append(rgb_msg); del self.pending[:-6]
        self.process_pending()

    def process_pending(self):
        """Detect cones in queued images once odometry for each image's own timestamp exists.

        The image is stamped when it was rendered; the odometry transform for that instant often
        arrives a little later. Using the latest (older) pose instead placed every cone of a
        frame rotated by yaw_rate x lag -- ~10 deg at 2 rad/s in the bends -- and the cone memory
        filled with phantom cones 0.5-0.9 m outside the track (found 2026-11-13 with the classical
        follower's debug log). So wait for the right pose; fall back to the latest only for an image
        that has waited longer than `tf_wait`.
        """
        while self.pending:
            rgb_msg = self.pending[0]
            age = self.now_s() - self.stamp_s(rgb_msg)
            # The depth image for this frame (same stamp, from oak_depth) arrives after the colour
            # image. Ranging with the previous frame's depth (66 ms older) read the floor or the
            # background behind each cone whenever the car turned: phantom cones 0.5-1 m too far.
            if not self.depth_for(rgb_msg) and age < self.tf_wait:
                return
            try:
                odom_base = self.tf.lookup_transform('odom', 'base_link', rgb_msg.header.stamp)
            except TransformException:
                if age < self.tf_wait:
                    return                      # pose for this image not here yet: try again later
                try:
                    odom_base = self.tf.lookup_transform('odom', 'base_link', Time())
                except TransformException:
                    odom_base = None
                # the latest pose stands in only if it is close in time to the image
                if odom_base is None or abs(self.stamp_s(odom_base) - self.stamp_s(rgb_msg)) > self.tf_fallback_max:
                    self.stats['tf_dropped'] += 1
                    self.pending.pop(0)
                    continue
                self.stats['tf_fallback'] += 1
            self.pending.pop(0)
            self.detect(rgb_msg, odom_base)

    def depth_for(self, rgb_msg):
        """The depth image taken with this colour image (same stamp, within depth_max_age)."""
        best = min(self.depths, key=lambda m: abs(self.stamp_s(m) - self.stamp_s(rgb_msg)), default=None)
        if best is not None and abs(self.stamp_s(best) - self.stamp_s(rgb_msg)) <= self.depth_max_age:
            return best
        return None

    def detect(self, rgb_msg, odom_base):
        try:
            cam = self.tf.lookup_transform('base_link', self.camera_frame, Time())
        except TransformException:
            return
        depth = None
        dmsg = self.depth_for(rgb_msg)
        if dmsg is not None:
            depth = self.bridge.imgmsg_to_cv2(dmsg).astype(np.float32)
            if dmsg.encoding == '16UC1':
                depth /= 1000.0
        else:
            self.stats['no_depth'] += 1
        dets = self.detector.detect(self.bridge.imgmsg_to_cv2(rgb_msg, 'bgr8'), depth)
        R, p = tf_matrix(cam)
        base = np.array([(R @ d.p_cam + p)[:2] for d in dets]).reshape(-1, 2)
        Ro, po = tf_matrix(odom_base)
        t_img = self.stamp_s(rgb_msg)            # capture time: processing late must not make it fresher
        self.memory.update(base @ Ro[:2, :2].T + po[:2], t_img)   # odom frame
        self.last_image = t_img if self.last_image is None else max(self.last_image, t_img)
        self.stats['images'] += 1; self.stats['dets'] += len(dets)
        self.stats['size_ranged'] += sum(d.method == 'size' for d in dets)
        self.stats['ground_ranged'] += sum(d.method == 'ground' for d in dets)

    def reset_history(self, forget_cones=False):
        self.prev_action = np.array([-1.0, 0.0], np.float32)
        self.follower.last, self.follower.lost_steps = (0.0, 0.0), 0
        if forget_cones:
            self.memory = ConeMemory(horizon=self.memory_s)

    def inputs(self, now):
        """(odom -> base_link transform, lag) if every input is fresh, else (None, why)."""
        if self.last_image is not None and now < self.last_image - 1.0:
            # Clock went backwards (simulation reset): odometry restarted too, and remembered cones
            # are stamped in the "future", so they would never age out. Forget them.
            self.last_image = None
            self.reset_history(forget_cones=True)
        if self.last_image is None or now - self.last_image >= self.image_timeout:
            return None, 'no recent camera image'
        if self.odom_stamp is None or now - self.odom_stamp > self.odom_timeout:
            return None, 'no recent odometry'
        try:
            tfm = self.tf.lookup_transform('odom', 'base_link', Time())
        except TransformException:
            return None, 'no odom -> base_link transform'
        lag = now - self.stamp_s(tfm)
        if lag > self.tf_timeout or lag < -self.tf_timeout:
            return None, f'odom -> base_link transform {lag:.2f} s old'
        return tfm, max(lag, 0.0)

    def step(self):
        self.process_pending()
        cmd = Twist()
        now = self.now_s()
        tfm, lag = self.inputs(now)          # lag (s), or why the inputs are not usable
        if tfm is not None:
            Ro, po = tf_matrix(tfm)
            yaw = math.atan2(Ro[1, 0], Ro[0, 0])
            # the latest odometry transform is `lag` seconds old: bring the pose up to now
            # (constant speed and yaw rate), or the cones are re-projected from where the car was
            po = po.copy()
            po[0] += self.v * lag * math.cos(yaw + self.yaw_rate * lag / 2)
            po[1] += self.v * lag * math.sin(yaw + self.yaw_rate * lag / 2)
            yaw += self.yaw_rate * lag
            self.stats['tf_lag_ms'] = max(self.stats.get('tf_lag_ms', 0), int(lag * 1000))
            rel, _ = self.memory.relative(po[0], po[1], yaw, now)
            action = self.follower.action(rel, self.v, self.yaw_rate)
            if self.debug is not None:
                f = self.follower
                self.debug.write(f"{self.get_clock().now().nanoseconds * 1e-9:.3f};{po[0]:.3f};{po[1]:.3f};{yaw:.4f};"
                                 f"{self.v:.3f};{self.yaw_rate:.3f};{int(f.fallback)};{action[0]:.3f};{action[1]:.3f};"
                                 f"{f.target};{np.round(f.path, 2).tolist()};{np.round(rel, 2).tolist()}\n")
            action = np.clip(action, -1, 1).astype(np.float32)
            action[1] = slew_steer(float(self.prev_action[1]), float(action[1]), CTRL_DT)   # servo slew
            v_cmd = min((float(action[0]) + 1) / 2 * V_MAX, self.speed_limit)
            steer_cmd = float(action[1]) * STEER_MAX
            self.prev_action = action
            cmd.linear.x = v_cmd
            # Gazebo's AckermannSteering plugin takes a yaw rate and turns it into a steering
            # angle with its own ramped speed, not the commanded one. Use the measured speed
            # (which tracks the ramp) so the plugin's angle equals the follower's; with the
            # commanded speed it steers harder while accelerating and softer while braking.
            cmd.angular.z = max(self.v, 0.0) * math.tan(steer_cmd) / WHEELBASE
        else:
            self.stats['stale_steps'] += 1
            why = lag
            self.warn(f'{why}; stopping')
            # without a trustworthy odom -> base_link the remembered cone positions are unusable
            self.reset_history(forget_cones='transform' in why)
        if rclpy.ok():
            self.pub.publish(cmd)


def main():
    rclpy.init()
    node = ConeFollowerNode()
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
