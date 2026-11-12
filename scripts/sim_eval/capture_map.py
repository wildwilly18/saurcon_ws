#!/usr/bin/env python3
"""Save the most recently received grid and loop-closure events during a run."""
import json
import sys
from pathlib import Path
import numpy as np
import cv2
import rclpy
from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from rtabmap_msgs.msg import Info
from rclpy.executors import ExternalShutdownException

rclpy.init();node=rclpy.create_node('capture_map');out=Path(sys.argv[1]);out.mkdir(exist_ok=True,parents=True)
closures=[]
(out/'closures.json').write_text('[]\n')
def grid(m):
    data=np.array(m.data,dtype=np.int16).reshape(m.info.height,m.info.width)
    pixels=np.where(data<0,127,255-data*255/100).astype(np.uint8)
    cv2.imwrite(str(out/'map.png'),np.flipud(pixels))
    (out/'map.json').write_text(json.dumps({'width':m.info.width,'height':m.info.height,'resolution':m.info.resolution,'occupied':int((data>50).sum()),'known':int((data>=0).sum())},indent=2))
def info(m):
    if m.loop_closure_id:
        closures.append({'stamp':m.header.stamp.sec+m.header.stamp.nanosec*1e-9,'reference':m.ref_id,'loop':m.loop_closure_id})
        (out/'closures.json').write_text(json.dumps(closures,indent=2))
node.create_subscription(OccupancyGrid,'/map',grid,QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE))
node.create_subscription(Info,'/rtabmap/info',info,10)
try:rclpy.spin(node)
except (KeyboardInterrupt,ExternalShutdownException):pass
finally:node.destroy_node()
