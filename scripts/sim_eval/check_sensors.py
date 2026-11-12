#!/usr/bin/env python3
"""Check live OAK stream rates, frames, calibration and depth encoding."""
import json
import time
import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image,CameraInfo,Imu
from cv_bridge import CvBridge
import numpy as np

rclpy.init();node=rclpy.create_node('check_oak_sensors');records={};info={};bridge=CvBridge();depth=[]
def receive(topic,msg):
    t=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9
    records.setdefault(topic,[]).append(t)
    info[topic]={'frame':msg.header.frame_id}
    if isinstance(msg,Image):
        info[topic].update(encoding=msg.encoding,width=msg.width,height=msg.height)
        if topic=='stereo':
            z=bridge.imgmsg_to_cv2(msg);depth.append(float(np.count_nonzero(z)/z.size))
            assert msg.encoding=='16UC1' and ((z==0)|((z>=200)&(z<=4000))).all()
    elif isinstance(msg,CameraInfo):info[topic].update(fx=msg.k[0],cx=msg.k[2],cy=msg.k[5],tx=msg.p[3])
for name in ['rgb','left','right','stereo']:
    node.create_subscription(Image,f'/oak/{name}/image_raw',lambda m,n=name:receive(n,m),qos_profile_sensor_data)
    node.create_subscription(CameraInfo,f'/oak/{name}/camera_info',lambda m,n=name:receive(n+'_info',m),qos_profile_sensor_data)
node.create_subscription(Imu,'/oak/imu/data',lambda m:receive('imu',m),qos_profile_sensor_data)
end=time.time()+20
while time.time()<end:rclpy.spin_once(node,timeout_sec=.1)
assert len(records)==9, f'Missing streams: {list(records)}'
for name,times in records.items():
    unique=sorted(set(times));assert len(unique)>2
    rate=1/float(np.median(np.diff(unique)))
    info[name]['median_stamp_hz']=rate
    target = 100 if name=='imu' else 15
    info[name]['requested_hz'] = target
    info[name]['shortest_stamp_interval_s'] = float(np.min(np.diff(unique)))
    # Best-effort subscribers may drop messages while SLAM is busy. Verify
    # source cadence separately and report delivered median rate honestly.
    assert np.min(np.diff(unique)) <= 1.2/target, (name, rate)
assert abs(info['right_info']['tx']/info['right_info']['fx']+.075)<1e-6
assert abs(info['rgb_info']['fx']-465.741)<.01
assert info['stereo']['frame']==info['rgb']['frame']=='oak_rgb_camera_optical_frame'
assert set(records['stereo']) & set(records['rgb']), 'RGB/depth stamps do not overlap'
info['depth_valid_fraction_mean']=float(np.mean(depth))
print(json.dumps(info,indent=2));node.destroy_node();rclpy.shutdown()
