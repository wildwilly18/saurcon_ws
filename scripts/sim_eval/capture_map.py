#!/usr/bin/env python3
"""Save the occupancy grid and loop-closure events during a run.

map.png / map.json: the most recent grid. maps/NNNN.png + maps/index.csv: every grid
received (stamp, origin, resolution), for videos of the map being built. The index is created
with the first grid, so a run without SLAM has no maps/index.csv.
cones_rtab.csv: the cone map of the RTAB-Map-posed cone mapper (cone_mapping:=rtab|both),
sampled every 0.5 s: stamp; x y; x y; ... in the map frame.
"""
import json
import sys
from pathlib import Path
import numpy as np
import cv2
import rclpy
from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseArray
from rtabmap_msgs.msg import Info
from rclpy.executors import ExternalShutdownException

rclpy.init();node=rclpy.create_node('capture_map');out=Path(sys.argv[1]);out.mkdir(exist_ok=True,parents=True)
closures=[]
(out/'closures.json').write_text('[]\n')
index=[None]
count=[0];cone_file=open(out/'cones_rtab.csv','w');last_cones=[-1.0]
def grid(m):
    data=np.array(m.data,dtype=np.int16).reshape(m.info.height,m.info.width)
    pixels=np.where(data<0,127,255-data*255/100).astype(np.uint8)
    cv2.imwrite(str(out/'map.png'),np.flipud(pixels))
    (out/'maps').mkdir(exist_ok=True)
    cv2.imwrite(str(out/'maps'/f'{count[0]:04d}.png'),np.flipud(pixels))
    if index[0] is None:
        (out/'maps').mkdir(exist_ok=True)
        index[0]=open(out/'maps'/'index.csv','w');index[0].write('frame,stamp,origin_x,origin_y,resolution,width,height\n')
    o=m.info.origin.position
    index[0].write(f"{count[0]},{m.header.stamp.sec+m.header.stamp.nanosec*1e-9:.3f},{o.x:.4f},{o.y:.4f},{m.info.resolution},{m.info.width},{m.info.height}\n");index[0].flush()
    count[0]+=1
    (out/'map.json').write_text(json.dumps({'width':m.info.width,'height':m.info.height,'resolution':m.info.resolution,'occupied':int((data>50).sum()),'known':int((data>=0).sum())},indent=2))
def info(m):
    if m.loop_closure_id:
        closures.append({'stamp':m.header.stamp.sec+m.header.stamp.nanosec*1e-9,'reference':m.ref_id,'loop':m.loop_closure_id})
        (out/'closures.json').write_text(json.dumps(closures,indent=2))
node.create_subscription(OccupancyGrid,'/map',grid,QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE))
node.create_subscription(Info,'/rtabmap/info',info,10)
def cones(m):
    t=m.header.stamp.sec+m.header.stamp.nanosec*1e-9
    if t-last_cones[0]<0.5: return
    last_cones[0]=t
    cone_file.write(f"{t:.3f};"+';'.join(f'{p.position.x:.3f} {p.position.y:.3f}' for p in m.poses)+'\n');cone_file.flush()
node.create_subscription(PoseArray,'/cones_rtab/map',cones,10)
try:rclpy.spin(node)
except (KeyboardInterrupt,ExternalShutdownException):pass
finally:node.destroy_node()
