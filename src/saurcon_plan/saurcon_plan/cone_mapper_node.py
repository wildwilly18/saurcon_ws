#!/usr/bin/env python3
"""Detect cones in the OAK-D images and build a cone map (Gazebo / real car).

Subscribes to the colour image and the depth image aligned to it, detects cones
(cones.ConeDetector), places each detection in the map frame using the chosen
pose source, and accumulates a cone map (cones.ConeMap).

pose_source:
  rtab  - the localization stack: TF map -> base_link (RTAB-Map + fused UKF) at the
          image timestamp. What the real car would use.
  truth - Gazebo ground truth (/gt_pose from scripts/sim_eval/gt_bridge.py),
          converted to the map frame with `map_origin`. Isolates detection error.

Publishes (in frame `map`): <ns>/detections (PoseArray, this frame's cones),
<ns>/map (PoseArray, confirmed cones), <ns>/markers (MarkerArray for RViz).
If `world` is set, the map is scored against the true cones every 5 s and the
score is written to `output_json`.
"""
import json
import math
from collections import deque
from pathlib import Path

import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import Pose, PoseArray
from message_filters import ApproximateTimeSynchronizer, Subscriber
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CameraInfo, Image
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker, MarkerArray

from saurcon_plan.cones import ConeDetector, ConeMap, planar, score
from saurcon_plan.track import Track

MODEL_TO_BASE = -0.127        # base_link (rear axle) is 0.127 m behind the Gazebo model origin


def quat_yaw(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def tf_matrix(t):
    q, p = t.transform.rotation, t.transform.translation
    x, y, z, w = q.x, q.y, q.z, q.w
    R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
    return R, np.array([p.x, p.y, p.z])


class ConeMapper(Node):
    def __init__(self):
        super().__init__('cone_mapper')
        self.source = self.declare_parameter('pose_source', 'rtab').value
        if self.source not in ('rtab', 'truth'):
            raise ValueError('pose_source must be rtab or truth')
        ox, oy, oyaw = self.declare_parameter('map_origin', [-1.127, 0.0, 0.0]).value
        self.origin = (ox, oy, oyaw)
        self.camera_frame = self.declare_parameter('camera_frame', 'oak_rgb_camera_optical_frame').value
        world = self.declare_parameter('world', '').value
        self.output_json = self.declare_parameter('output_json', '').value
        self.detector = None
        self.cmap = ConeMap()
        self.true_map = None
        if world:
            # True cones in the map frame, for scoring only.
            c, s = math.cos(-oyaw), math.sin(-oyaw)
            w = Track.from_world(world).cones - np.array([ox, oy])
            self.true_map = np.column_stack([c * w[:, 0] - s * w[:, 1], s * w[:, 0] + c * w[:, 1]])
        self.bridge = CvBridge()
        self.tf = Buffer(); self.tf_listener = TransformListener(self.tf, self)
        self.gt = deque(maxlen=400)
        if self.source == 'truth':
            self.create_subscription(TFMessage, '/gt_pose', self.on_gt, 50)
        self.create_subscription(CameraInfo, '/oak/rgb/camera_info', self.on_info, 10)
        rgb = Subscriber(self, Image, '/oak/rgb/image_raw', qos_profile=qos_profile_sensor_data)
        depth = Subscriber(self, Image, '/oak/stereo/image_raw', qos_profile=qos_profile_sensor_data)
        self.sync = ApproximateTimeSynchronizer([rgb, depth], 10, 0.03)
        self.sync.registerCallback(self.on_images)
        self.pub_det = self.create_publisher(PoseArray, '~/detections', 10)
        self.pub_map = self.create_publisher(PoseArray, '~/map', 10)
        self.pub_markers = self.create_publisher(MarkerArray, '~/markers', 10)
        self.create_timer(5.0, self.report)
        self.frames = self.detections = 0
        self.get_logger().info(f'cone mapper: pose source {self.source}')

    def on_info(self, msg):
        if self.detector is None:
            K = msg.k
            self.detector = ConeDetector(K[0], K[4], K[2], K[5])
            self.get_logger().info(f'camera fx {K[0]:.1f} fy {K[4]:.1f} cx {K[2]:.1f} cy {K[5]:.1f}')

    def on_gt(self, msg):
        t = msg.transforms[0]
        yaw = quat_yaw(t.transform.rotation)
        x = t.transform.translation.x + MODEL_TO_BASE * math.cos(yaw)
        y = t.transform.translation.y + MODEL_TO_BASE * math.sin(yaw)
        self.gt.append((Time.from_msg(t.header.stamp).nanoseconds * 1e-9, x, y, yaw))

    def base_pose_in_map(self, stamp):
        """(x, y, yaw) of base_link in the map frame at `stamp`, or None."""
        if self.source == 'rtab':
            try:
                t = self.tf.lookup_transform('map', 'base_link', stamp)
            except TransformException:
                return None
            return (t.transform.translation.x, t.transform.translation.y, quat_yaw(t.transform.rotation))
        if not self.gt:
            return None
        ts = Time.from_msg(stamp).nanoseconds * 1e-9
        best = min(self.gt, key=lambda g: abs(g[0] - ts))
        if abs(best[0] - ts) > 0.1:
            return None
        ox, oy, oyaw = self.origin
        dx, dy = best[1] - ox, best[2] - oy
        c, s = math.cos(-oyaw), math.sin(-oyaw)
        return (c * dx - s * dy, s * dx + c * dy, best[3] - oyaw)

    def on_images(self, rgb_msg, depth_msg):
        if self.detector is None:
            return
        try:
            cam = self.tf.lookup_transform('base_link', self.camera_frame, Time())
        except TransformException:
            return
        pose = self.base_pose_in_map(rgb_msg.header.stamp)
        if pose is None:
            return
        bgr = self.bridge.imgmsg_to_cv2(rgb_msg, 'bgr8')
        depth = self.bridge.imgmsg_to_cv2(depth_msg).astype(np.float32)
        if depth_msg.encoding == '16UC1':
            depth /= 1000.0
        dets = self.detector.detect(bgr, depth)
        self.frames += 1
        if not dets:
            return
        R, p = tf_matrix(cam)
        base = np.array([R @ d.p_cam + p for d in dets])[:, :2]
        pts = planar(pose, base)
        self.cmap.update(pts, [d.range for d in dets])
        self.detections += len(dets)
        self.publish(rgb_msg.header.stamp, pts)

    def poses(self, stamp, xy):
        msg = PoseArray(); msg.header.frame_id = 'map'; msg.header.stamp = stamp
        for x, y in xy:
            p = Pose(); p.position.x, p.position.y = float(x), float(y); p.orientation.w = 1.0
            msg.poses.append(p)
        return msg

    def publish(self, stamp, det_xy):
        self.pub_det.publish(self.poses(stamp, det_xy))
        cones = self.cmap.cones()
        self.pub_map.publish(self.poses(stamp, cones))
        arr = MarkerArray()
        for i, (x, y) in enumerate(cones):
            m = Marker(); m.header.frame_id = 'map'; m.header.stamp = stamp; m.ns = 'cones'; m.id = i
            m.type = Marker.CYLINDER; m.pose.position.x, m.pose.position.y = float(x), float(y)
            m.pose.position.z = 0.035; m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = 0.04; m.scale.z = 0.07
            m.color.r, m.color.g, m.color.b, m.color.a = 1.0, 0.4, 0.0, 1.0
            arr.markers.append(m)
        self.pub_markers.publish(arr)

    def report(self):
        cones = self.cmap.cones()
        res = {'pose_source': self.source, 'frames': self.frames, 'detections': self.detections}
        if self.true_map is not None:
            res.update(score(cones, self.true_map))
        self.get_logger().info(json.dumps(res))
        if self.output_json:
            Path(self.output_json).write_text(json.dumps(
                {**res, 'cones_map_frame': np.round(cones, 3).tolist()}, indent=1))


def main():
    rclpy.init()
    node = ConeMapper()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.report()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
