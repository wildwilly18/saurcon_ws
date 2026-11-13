#!/usr/bin/env python3
"""Render the actual Gazebo vehicle from fixed studio cameras, without ROS/control.

Source /opt/ros/jazzy/setup.bash, then run:
  python3 scripts/sim_eval/preview_vehicle.py evaluation/vehicle_visuals/after

Uses its own Gazebo partition and a static include in a temporary preview world.
The source model's physics, sensors and poses are not edited. --models can point
at a directory containing an earlier copy of both vehicle and OAK-D models.
"""
import argparse
import math
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def world_text():
    views = {
        'front_three_quarter': ((.53, -.48, .30), (.015, 0, .065), .72),
        'front': ((.65, -.015, .21), (.03, 0, .065), .60),
        'rear_three_quarter': ((-.51, .44, .29), (-.015, 0, .065), .72),
        'side': ((.01, -.70, .24), (.01, 0, .065), .70),
    }
    cameras = []
    for name, (eye, target, fov) in views.items():
        dx, dy, dz = (b-a for a, b in zip(eye, target))
        yaw = math.atan2(dy, dx)
        pitch = -math.atan2(dz, math.hypot(dx, dy))
        cameras.append(f'''<model name="preview_{name}"><static>true</static>
          <pose>{' '.join(map(str, eye))} 0 {pitch} {yaw}</pose><link name="camera">
          <sensor name="camera" type="camera"><topic>/preview/{name}</topic>
          <always_on>true</always_on><update_rate>5</update_rate><camera>
          <horizontal_fov>{fov}</horizontal_fov><image><width>1280</width><height>900</height>
          <format>R8G8B8</format></image><clip><near>0.01</near><far>20</far></clip>
          </camera></sensor></link></model>''')
    return f'''<?xml version="1.0"?><sdf version="1.9"><world name="vehicle_preview">
      <physics name="preview" type="ignored"><max_step_size>0.01</max_step_size><real_time_factor>1</real_time_factor></physics>
      <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
      <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>
      <scene><ambient>0.40 0.40 0.40 1</ambient><background>0.82 0.84 0.86 1</background><shadows>true</shadows></scene>
      <light name="key" type="directional"><pose>2 -3 4 0 0 0</pose><direction>-0.4 0.5 -1</direction>
        <diffuse>0.85 0.82 0.78 1</diffuse><specular>0.35 0.35 0.35 1</specular><cast_shadows>true</cast_shadows></light>
      <light name="fill" type="directional"><direction>0.4 -0.4 -0.6</direction>
        <diffuse>0.28 0.31 0.36 1</diffuse><specular>0.1 0.1 0.1 1</specular><cast_shadows>false</cast_shadows></light>
      <model name="floor"><static>true</static><link name="floor"><visual name="floor"><geometry>
        <plane><normal>0 0 1</normal><size>200 200</size></plane></geometry>
        <material><ambient>0.56 0.55 0.53 1</ambient><diffuse>0.56 0.55 0.53 1</diffuse><specular>0 0 0 1</specular></material>
      </visual></link></model>
      <include><uri>model://rc_ackermann_vehicle</uri><name>rc_vehicle</name><static>true</static><pose>0 0 .003 0 0 0</pose></include>
      {''.join(cameras)}
    </world></sdf>''', views


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out', type=Path)
    parser.add_argument('--models', type=Path, default=ROOT / 'src/middle_earth/models')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    os.environ['GZ_PARTITION'] = f'saurcon_visual_preview_{os.getpid()}'
    os.environ['GZ_SIM_RESOURCE_PATH'] = str(args.models.resolve())
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image
    node = Node()
    text, views = world_text()
    counts = dict.fromkeys([*views, 'onboard'], 0)

    def receive(name):
        def callback(msg):
            counts[name] += 1
            if counts[name] >= 4:
                image = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.width, 3)
                cv2.imwrite(str(args.out / f'{name}.png'), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        return callback

    topics = {name: f'/preview/{name}' for name in views}
    topics['onboard'] = '/oak_sim/rgb/image'
    for name, topic in topics.items():
        if not node.subscribe(Image, topic, receive(name)):
            raise RuntimeError(f'Cannot subscribe to {topic}')
    with tempfile.TemporaryDirectory(prefix='saurcon-preview-') as tmp:
        world = Path(tmp) / 'preview.sdf'; world.write_text(text)
        with (args.out / 'gazebo.log').open('w') as log:
            proc = subprocess.Popen(['gz', 'sim', '-s', '-r', '--headless-rendering', str(world)],
                                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                deadline = time.monotonic() + 90
                while min(counts.values()) < 6:
                    if proc.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError(f'Preview failed: {counts}; see {args.out / "gazebo.log"}')
                    time.sleep(.1)
            finally:
                os.killpg(proc.pid, signal.SIGINT) if proc.poll() is None else None
                try:
                    proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL); proc.wait()
    for topic in topics.values():
        node.unsubscribe(topic)
    print(f'Saved {len(counts)} Gazebo camera views to {args.out}')


if __name__ == '__main__':
    main()
