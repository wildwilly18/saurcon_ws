#!/usr/bin/env python3
"""Check the actual OAK model's rendered centre depth against a planar wall."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import numpy as np

p=argparse.ArgumentParser();p.add_argument('distance',type=float);a=p.parse_args()
os.environ['GZ_PARTITION']=f'saurcon_wall_{os.getpid()}'
ws=Path(__file__).resolve().parents[2]
os.environ['GZ_SIM_RESOURCE_PATH']=str(ws/'src/middle_earth/models')
from gz.transport13 import Node
from gz.msgs10.image_pb2 import Image

world=f'''<sdf version="1.9"><world name="wall_test">
<plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
<plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>
<include><uri>model://oak_d_lite</uri><name>oak</name><static>true</static><pose>0 0 1 0 0 0</pose></include>
<model name="wall"><static>true</static><pose>{a.distance+.05} 0 1 0 0 0</pose><link name="wall">
<visual name="wall"><geometry><box><size>0.1 10 10</size></box></geometry></visual></link></model>
</world></sdf>'''
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'wall.sdf';path.write_text(world)
    log=(Path(tmp)/'gazebo.log').open('w')
    process=subprocess.Popen(['gz','sim','-s','-r','--headless-rendering',str(path)],stdout=log,stderr=log,start_new_session=True)
    node=Node();values=[]
    def cb(msg):
        if msg.width!=640 or msg.height!=400:return
        z=np.frombuffer(msg.data,dtype=np.float32).reshape(msg.height,-1)[:,:msg.width]
        values.append(float(np.median(z[195:205,315:325])))
    node.subscribe(Image,'/oak_sim/rgb/depth_image',cb)
    try:
        end=time.monotonic()+25
        while len(values)<3 and time.monotonic()<end:time.sleep(.1)
        if not values:raise RuntimeError('No depth received: '+(Path(tmp)/'gazebo.log').read_text()[-1500:])
        measured=float(np.median(values))
        assert abs(measured-a.distance)<.015,(a.distance,measured)
        print(json.dumps({'wall_m':a.distance,'measured_m':measured,'samples':len(values)}))
    finally:
        node.unsubscribe('/oak_sim/rgb/depth_image')
        os.killpg(process.pid,signal.SIGINT)
        try:process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);process.wait()
        log.close()
