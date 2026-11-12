#!/usr/bin/env python3
"""Bridge only the vehicle pose, preserving Gazebo Pose_V names and timestamps."""
import rclpy
from rclpy.node import Node as RosNode
from rclpy.executors import ExternalShutdownException
from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V
from geometry_msgs.msg import TransformStamped
from tf2_msgs.msg import TFMessage

class GroundTruth(RosNode):
    def __init__(self):
        super().__init__('ground_truth_bridge')
        self.pub=self.create_publisher(TFMessage,'/gt_pose',50)
        self.gz=GzNode()
        if not self.gz.subscribe(Pose_V,'/world/warehouse_racetrack/dynamic_pose/info',self.receive):
            raise RuntimeError('Cannot subscribe to Gazebo ground truth')
    def receive(self,msg):
        for pose in msg.pose:
            if pose.name!='rc_vehicle':continue
            tf=TransformStamped();tf.header.frame_id='world';tf.child_frame_id=pose.name
            tf.header.stamp.sec=msg.header.stamp.sec;tf.header.stamp.nanosec=msg.header.stamp.nsec
            for key in ('x','y','z'):setattr(tf.transform.translation,key,getattr(pose.position,key))
            for key in ('x','y','z','w'):setattr(tf.transform.rotation,key,getattr(pose.orientation,key))
            if rclpy.ok():self.pub.publish(TFMessage(transforms=[tf]))

rclpy.init();node=GroundTruth()
try:rclpy.spin(node)
except (KeyboardInterrupt,ExternalShutdownException):pass
finally:
    node.gz.unsubscribe('/world/warehouse_racetrack/dynamic_pose/info')
    node.destroy_node()
    if rclpy.ok():rclpy.shutdown()
