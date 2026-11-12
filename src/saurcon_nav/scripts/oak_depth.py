#!/usr/bin/env python3
"""Approximate passive stereo depth, preserving RGB-D capture timestamps."""
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from message_filters import Subscriber, TimeSynchronizer


def degrade_depth(depth, gray, rng, minimum=0.2, maximum=4.0,
                  disparity_std=0.25, texture_threshold=2.0):
    """Millimetre uint16 depth; zeros denote invalid matches, not free space."""
    z = np.asarray(depth, dtype=np.float32)
    valid = np.isfinite(z) & (z >= minimum) & (z <= maximum)
    # Local contrast proxy, not an actual stereo matcher. Smooth image noise first.
    g = cv2.GaussianBlur(gray.astype(np.float32), (5, 5), 0)
    mean = cv2.boxFilter(g, -1, (9, 9))
    contrast = np.sqrt(np.maximum(cv2.boxFilter(g*g, -1, (9, 9))-mean*mean, 0))
    valid &= (contrast >= texture_threshold)
    # sigma_z = z^2 sigma_disparity / (f_mono * baseline).
    sigma = np.where(valid, z, 0)**2 * disparity_std / (432.0 * 0.075)
    noisy = np.where(valid, z, 0) + rng.normal(size=z.shape) * sigma
    valid &= (noisy >= minimum) & (noisy <= maximum)
    return np.where(valid, np.rint(noisy*1000), 0).astype(np.uint16)


class OakDepth(Node):
    def __init__(self):
        super().__init__('oak_depth')
        self.bridge = CvBridge()
        self.rng = np.random.default_rng(self.declare_parameter('seed', 42).value)
        self.params = {key: self.declare_parameter(key, val).value for key, val in
                       [('minimum', .2), ('maximum', 4.0), ('disparity_std', .25),
                        ('texture_threshold', 2.0)]}
        self.pub = self.create_publisher(Image, '/oak/stereo/image_raw', 10)
        self.legacy = self.create_publisher(Image, '/camera/depth_image', 10)
        self.rgb = Subscriber(self, Image, '/oak/rgb/image_raw', qos_profile=qos_profile_sensor_data)
        self.depth = Subscriber(self, Image, '/oak_sim/depth', qos_profile=qos_profile_sensor_data)
        self.sync = TimeSynchronizer([self.rgb, self.depth], 20)
        self.sync.registerCallback(self.process)
        self.info_pubs = {}
        for name in ('rgb', 'left', 'right'):
            self.info_pubs[name] = self.create_publisher(CameraInfo, f'/oak/{name}/camera_info', 10)
            self.create_subscription(CameraInfo, f'/oak_sim/{name}/camera_info',
                                     lambda msg, name=name: self.info(msg, name), qos_profile_sensor_data)
        self.stereo_info = self.create_publisher(CameraInfo, '/oak/stereo/camera_info', 10)
        self.legacy_info = self.create_publisher(CameraInfo, '/camera/camera_info', 10)

    def info(self, msg, name):
        msg.header.frame_id = f'oak_{name}_camera_optical_frame'
        # Rectified right camera projection relative to the left camera.
        if name == 'right': msg.p[3] = -msg.p[0] * .075
        self.info_pubs[name].publish(msg)
        if name == 'rgb':
            self.stereo_info.publish(msg)
            self.legacy_info.publish(msg)

    def process(self, rgb, depth):
        gray = self.bridge.imgmsg_to_cv2(rgb, 'mono8')
        z = self.bridge.imgmsg_to_cv2(depth, '32FC1')
        out = self.bridge.cv2_to_imgmsg(degrade_depth(z, gray, self.rng, **self.params), '16UC1')
        out.header = rgb.header
        self.pub.publish(out)
        self.legacy.publish(out)


def main():
    rclpy.init()
    node = OakDepth()
    try: rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException): pass
    finally:
        node.destroy_node()
        if rclpy.ok(): rclpy.shutdown()


if __name__ == '__main__': main()
