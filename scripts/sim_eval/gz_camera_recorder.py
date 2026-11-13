#!/usr/bin/env python3
"""Record a Gazebo camera topic to JPEG frames plus a timestamp list (no ROS needed).

usage: gz_camera_recorder.py <gz-topic> <output-dir>    e.g. /chase/image run/chase
Run in the simulation's GZ_PARTITION (runsim.sh starts it when CHASE=1).
"""
import signal
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from gz.msgs10.image_pb2 import Image
from gz.transport13 import Node

topic, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
stamps = open(out / 'stamps.csv', 'w'); stamps.write('frame,t\n')
count = [0]


def on_image(msg):
    img = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, -1)
    cv2.imwrite(str(out / f'{count[0]:06d}.jpg'), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    stamps.write(f'{count[0]},{msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9:.4f}\n'); stamps.flush()
    count[0] += 1


node = Node()
if not node.subscribe(Image, topic, on_image):
    sys.exit(f'cannot subscribe to {topic}')
running = [True]
signal.signal(signal.SIGINT, lambda *_: running.__setitem__(0, False))
signal.signal(signal.SIGTERM, lambda *_: running.__setitem__(0, False))
while running[0]:
    time.sleep(0.2)
stamps.close()
print(f'{count[0]} frames from {topic}')
