"""MuJoCo (MJCF) model of the SAURCON car, optionally with the cone raceway.

Geometry and masses follow the Gazebo model
(src/middle_earth/models/rc_ackermann_vehicle/model.sdf):
  wheelbase 0.254 m, track 0.165 m, wheel radius 0.033 m, width 0.04 m,
  chassis 4.0 kg, wheels 0.3 kg each, steering knuckles 0.1 kg each,
  steering joints limited to +/-0.5 rad.
Tyre friction 1.4 is calibrated so the grip plateau matches Gazebo's (~10 m/s^2
lateral); Gazebo's friction pyramid gives more grip than its nominal mu of 1.0.
Drive: velocity actuators on the rear wheels (torque-limited, so they can spin).
Steering: position actuators on the two knuckles (Ackermann angles set by the env).

Collision groups (MuJoCo collides two geoms if contype & conaffinity overlap):
  floor 1/1, wheels 1/1, chassis 2/2, cones 3/3 -> wheels touch floor and cones,
  the chassis touches only cones, cones touch everything.
"""
import math

import numpy as np

WHEELBASE = 0.254
TRACK = 0.165
WHEEL_R = 0.033
WHEEL_W = 0.04
STEER_JOINT_LIMIT = 0.5
REAR_AXLE_X = -0.127          # base_link (rear-axle centre) in the chassis body frame


def _cone_mesh(r=0.0134, h=0.068, n=16):
    pts = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 0.0) for i in range(n)]
    pts.append((0.0, 0.0, h))
    return ' '.join(f'{x:.5f} {y:.5f} {z:.5f}' for x, y, z in pts)


def build_mjcf(cones=None, cone_mode='visual', friction=1.4, drive_torque=2.0,
               steer_kp=4.0, steer_damping=0.08, timestep=0.002):
    """Return an MJCF string.

    cones      -- (N, 2) array of cone positions, or None for an empty floor.
    cone_mode  -- 'visual' (drawn only, no physics cost) or 'physical' (24 g free bodies).
    """
    wheel_fric = f'{friction} 0.01 0.0001'
    rear = ''.join(f'''
      <body name="{side}_rear_wheel" pos="{REAR_AXLE_X} {y:.5f} {0.03 - 0.003:.4f}">
        <joint name="{side}_rear_spin" type="hinge" axis="0 1 0" damping="0.0001"/>
        <geom class="wheel" mass="0.3"/>
      </body>''' for side, y in (('left', TRACK / 2), ('right', -TRACK / 2)))
    front = ''.join(f'''
      <body name="{side}_knuckle" pos="{-REAR_AXLE_X} {y:.5f} {0.04 - 0.003:.4f}">
        <joint name="{side}_steer" type="hinge" axis="0 0 1" range="{-STEER_JOINT_LIMIT} {STEER_JOINT_LIMIT}" damping="{steer_damping}"/>
        <geom type="sphere" size="0.008" mass="0.1" contype="0" conaffinity="0" rgba="0.3 0.3 0.3 1"/>
        <body name="{side}_front_wheel" pos="0 0 -0.01">
          <joint name="{side}_front_spin" type="hinge" axis="0 1 0" damping="0.0001"/>
          <geom class="wheel" mass="0.3"/>
        </body>
      </body>''' for side, y in (('left', TRACK / 2), ('right', -TRACK / 2)))
    cone_xml, cone_asset = '', ''
    if cones is not None and len(cones):
        cone_asset = f'<mesh name="cone" vertex="{_cone_mesh()}"/>'
        for k, (x, y) in enumerate(np.asarray(cones)):
            if cone_mode == 'physical':
                cone_xml += f'''
    <body name="cone{k}" pos="{x:.4f} {y:.4f} 0">
      <freejoint/>
      <geom type="box" size="0.018 0.018 0.0015" pos="0 0 0.0015" mass="0.004" rgba="0.08 0.08 0.08 1" class="cone"/>
      <geom type="cylinder" size="0.008 0.027" pos="0 0 0.03" mass="0.02" class="cone" rgba="0 0 0 0"/>
      <geom type="mesh" mesh="cone" pos="0 0 0.003" mass="0" contype="0" conaffinity="0" rgba="0.85 0.2 0 1"/>
    </body>'''
            else:
                cone_xml += f'''
    <geom type="mesh" mesh="cone" pos="{x:.4f} {y:.4f} 0" contype="0" conaffinity="0" rgba="0.85 0.2 0 1"/>'''
    return f'''<mujoco model="saurcon_raceway">
  <compiler angle="radian" autolimits="true"/>
  <option timestep="{timestep}" integrator="implicitfast"/>
  <visual><global offwidth="960" offheight="540"/><quality shadowsize="2048"/></visual>
  <asset>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.55 0.55 0.53" rgb2="0.5 0.5 0.48" width="512" height="512"/>
    <material name="floor" texture="grid" texrepeat="40 40"/>
    {cone_asset}
  </asset>
  <default>
    <default class="wheel">
      <!-- Ellipsoid wheels give a single smooth contact point. (The car once bounced
           off the floor; the cause was the drive gain kv=5, not the wheel shape.) -->
      <geom type="ellipsoid" size="{WHEEL_R} {WHEEL_W / 2} {WHEEL_R}" friction="{wheel_fric}"
            condim="4" contype="1" conaffinity="1" rgba="0.1 0.1 0.1 1"/>
    </default>
    <default class="cone"><geom contype="3" conaffinity="3" friction="0.8 0.01 0.0001"/></default>
  </default>
  <worldbody>
    <light pos="0 0 6" dir="0 0 -1" diffuse="0.8 0.8 0.8"/>
    <geom name="floor" type="plane" size="60 60 0.1" material="floor" friction="1.0 0.01 0.0001" contype="1" conaffinity="1"/>
    <body name="car" pos="0 0 0.006">
      <freejoint name="car_free"/>
      <geom name="chassis" type="box" size="0.2 0.1 0.02" pos="0 0 0.037" mass="4.0" contype="2" conaffinity="2" rgba="0.15 0.35 0.75 1"/>
      <site name="base_link" pos="{REAR_AXLE_X} 0 0.037" size="0.01"/>
      <camera name="chase" mode="trackcom" pos="-1.2 0 0.6" xyaxes="0 -1 0 0.45 0 0.9"/>
      <!-- OAK-D Lite colour camera: 0.219 m ahead of base_link and 0.137 m above the floor
           (as fitted on Gazebo frames; chassis origin is 0.006 m up), looking forward, 640x400,
           1.204 rad horizontal FOV -> fovy = 2 atan(200 / 465.7) = 46.5 deg -->
      <camera name="oak_rgb" pos="{REAR_AXLE_X + 0.219:.3f} 0 0.131" xyaxes="0 -1 0 0 0 1" fovy="46.5"/>{rear}{front}
    </body>{cone_xml}
  </worldbody>
  <actuator>
    <!-- kv must stay low: kv=5 slammed the torque between its limits on the light
         wheels and made the car hop off the floor (tested 2026-11-12). -->
    <velocity name="left_drive"  joint="left_rear_spin"  kv="1" forcerange="{-drive_torque} {drive_torque}"/>
    <velocity name="right_drive" joint="right_rear_spin" kv="1" forcerange="{-drive_torque} {drive_torque}"/>
    <position name="left_steer"  joint="left_steer"  kp="{steer_kp}" ctrlrange="{-STEER_JOINT_LIMIT} {STEER_JOINT_LIMIT}"/>
    <position name="right_steer" joint="right_steer" kp="{steer_kp}" ctrlrange="{-STEER_JOINT_LIMIT} {STEER_JOINT_LIMIT}"/>
  </actuator>
</mujoco>'''


def ackermann(delta):
    """Inner/outer wheel angles for a bicycle steering angle delta; returns (left, right)."""
    if abs(delta) < 1e-6:
        return 0.0, 0.0
    R = WHEELBASE / math.tan(delta)                # signed turn radius at the rear axle
    left = math.atan(WHEELBASE / (R - TRACK / 2))
    right = math.atan(WHEELBASE / (R + TRACK / 2))
    lim = STEER_JOINT_LIMIT
    return float(np.clip(left, -lim, lim)), float(np.clip(right, -lim, lim))
