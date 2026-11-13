#!/usr/bin/env python3
"""Record simulation timestamps and map TF at each odometry timestamp."""
import csv
import math
import sys
from pathlib import Path
import cv2
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.qos import qos_profile_sensor_data
from rclpy.executors import ExternalShutdownException
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from nav_msgs.msg import Path as NavPath
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformListener, TransformException


def stamp(h): return h.stamp.sec+h.stamp.nanosec*1e-9

def yaw(q): return math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))


class Logger(Node):
    def __init__(self,out):
        super().__init__('run_logger',parameter_overrides=[rclpy.parameter.Parameter('use_sim_time',value=True)])
        self.out=out; (out/'frames').mkdir(parents=True)
        self.file=(out/'log.csv').open('w',newline='');self.csv=csv.writer(self.file)
        self.csv.writerow(['t','kind','a','b','c','d','e','f','g'])
        self.bridge=CvBridge();self.count=0;self.last_gt=-1.;self.pending=[]
        self.tf=Buffer();self.listener=TransformListener(self.tf,self)
        self.create_subscription(TFMessage,'/gt_pose',self.gt,50)
        self.create_subscription(Odometry,'/saurcon/nav_state',self.nav,50)
        self.create_subscription(PoseWithCovarianceStamped,'/saurcon/aruco_localization',self.loc,50)
        # SLAM fusion: RTAB-Map's own pose and the odometry-only UKF (when running)
        self.create_subscription(PoseWithCovarianceStamped,'/rtabmap/localization_pose',self.rtab,50)
        self.create_subscription(Odometry,'/saurcon/nav_state_odom',self.odomukf,50)
        self.create_subscription(NavPath,'/rtabmap/mapPath',self.rtabpath,10)
        self.last_path_stamp=None
        self.create_subscription(Image,'/camera/image',self.img,qos_profile_sensor_data)
        self.create_timer(.1,self.flush)

    def gt(self,msg):
        for index, tf in enumerate(msg.transforms):
            # Harmonic Pose_V bridge drops names/stamps: the first pose is the
            # only top-level dynamic vehicle in this world. Fall back explicitly.
            if tf.child_frame_id not in ('rc_vehicle','rc_ackermann_vehicle') and not (index == 0 and not tf.child_frame_id): continue
            t=stamp(tf.header) or self.get_clock().now().nanoseconds*1e-9
            if t-self.last_gt<.04:return
            self.last_gt=t;y=yaw(tf.transform.rotation);p=tf.transform.translation
            self.csv.writerow([t,'gt',p.x-.127*math.cos(y),p.y-.127*math.sin(y),y])

    def nav(self,msg):
        p=msg.pose.pose
        c=msg.pose.covariance
        # x, y, yaw, speed, then the filter's variances of x, y and yaw
        self.csv.writerow([stamp(msg.header),'nav',p.position.x,p.position.y,yaw(p.orientation),msg.twist.twist.linear.x,c[0],c[7],c[35]])
        self.pending.append(msg.header.stamp)
        self.pending=self.pending[-100:]

    def rtab(self,msg):
        p=msg.pose.pose;c=msg.pose.covariance
        self.csv.writerow([stamp(msg.header),'rtab',p.position.x,p.position.y,yaw(p.orientation),0.0,c[0],c[7],c[35]])
    def rtabpath(self,msg):
        if not msg.poses: return
        q=msg.poses[-1]; t=stamp(q.header) or stamp(msg.header)
        if t==self.last_path_stamp: return
        self.last_path_stamp=t; p=q.pose
        self.csv.writerow([t,'rtab',p.position.x,p.position.y,yaw(p.orientation),0.0,0.0,0.0,0.0])
    def odomukf(self,msg):
        p=msg.pose.pose;c=msg.pose.covariance
        self.csv.writerow([stamp(msg.header),'odomukf',p.position.x,p.position.y,yaw(p.orientation),msg.twist.twist.linear.x,c[0],c[7],c[35]])
    def loc(self,msg):
        p=msg.pose.pose;self.csv.writerow([stamp(msg.header),'aruco',p.position.x,p.position.y,yaw(p.orientation)])

    def img(self,msg):
        cv2.imwrite(str(self.out/'frames'/f'{self.count:06d}.jpg'),self.bridge.imgmsg_to_cv2(msg,'bgr8'))
        self.csv.writerow([stamp(msg.header),'frame',self.count]);self.count+=1

    def flush(self):
        pending=[]
        for stamp_msg in self.pending:
            try:
                tf=self.tf.lookup_transform('map','base_link',Time.from_msg(stamp_msg))
                p=tf.transform.translation
                self.csv.writerow([stamp_msg.sec+stamp_msg.nanosec*1e-9,'map',p.x,p.y,yaw(tf.transform.rotation)])
            except TransformException: pending.append(stamp_msg)
        self.pending=pending;self.file.flush()


def main():
    rclpy.init();node=Logger(Path(sys.argv[1]))
    try:rclpy.spin(node)
    except (KeyboardInterrupt,ExternalShutdownException):pass
    finally:
        node.file.close();node.destroy_node()
        if rclpy.ok():rclpy.shutdown()


if __name__=='__main__':main()
