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
        <geom class="tyre"/><geom class="rim"/><geom class="spoke"/><geom class="spoke" euler="1.5708 0 1.5708"/>
      </body>''' for side, y in (('left', TRACK / 2), ('right', -TRACK / 2)))
    front = ''.join(f'''
      <body name="{side}_knuckle" pos="{-REAR_AXLE_X} {y:.5f} {0.04 - 0.003:.4f}">
        <joint name="{side}_steer" type="hinge" axis="0 0 1" range="{-STEER_JOINT_LIMIT} {STEER_JOINT_LIMIT}" damping="{steer_damping}"/>
        <geom type="sphere" size="0.008" mass="0.1" contype="0" conaffinity="0" rgba="0.2 0.2 0.22 1"/>
        <body name="{side}_front_wheel" pos="0 0 -0.01">
          <joint name="{side}_front_spin" type="hinge" axis="0 1 0" damping="0.0001"/>
          <geom class="wheel" mass="0.3"/>
          <geom class="tyre"/><geom class="rim"/><geom class="spoke"/><geom class="spoke" euler="1.5708 0 1.5708"/>
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
    <geom type="box" size="0.018 0.018 0.0015" pos="{x:.4f} {y:.4f} 0.0015" contype="0" conaffinity="0" rgba="0.06 0.06 0.06 1"/>
    <geom type="mesh" mesh="cone" pos="{x:.4f} {y:.4f} 0.003" contype="0" conaffinity="0" rgba="0.85 0.2 0 1"/>'''
    return f'''<mujoco model="saurcon_raceway">
  <compiler angle="radian" autolimits="true"/>
  <option timestep="{timestep}" integrator="implicitfast"/>
  <visual>
    <global offwidth="1280" offheight="720"/>
    <headlight ambient="0.35 0.35 0.35" diffuse="0.45 0.45 0.45" specular="0.1 0.1 0.1"/>
    <quality shadowsize="4096"/>
    <map haze="0.15"/>
  </visual>
  <asset>
    <texture name="sky" type="skybox" builtin="gradient" rgb1="0.62 0.74 0.88" rgb2="0.93 0.95 0.98" width="512" height="512"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.56 0.56 0.54" rgb2="0.52 0.52 0.5" width="512" height="512"
             mark="edge" markrgb="0.6 0.6 0.58"/>
    <material name="floor" texture="grid" texrepeat="60 60" reflectance="0"/>
    <!-- Visual-only car materials. Deep blue body: nothing on the car can be mistaken for the
         red-orange cones by the detector. -->
    <material name="body" rgba="0.08 0.22 0.62 1" specular="0.7" shininess="0.7"/>
    <material name="stripe" rgba="0.95 0.95 0.95 1" specular="0.5"/>
    <material name="carbon" rgba="0.07 0.07 0.08 1" specular="0.3" shininess="0.3"/>
    <material name="glass" rgba="0.12 0.16 0.22 0.9" specular="1" shininess="1"/>
    <material name="tyre" rgba="0.04 0.04 0.04 1" specular="0.05"/>
    <material name="rim" rgba="0.78 0.78 0.82 1" specular="0.9" shininess="0.9"/>
    <material name="oak" rgba="0.25 0.26 0.28 1" specular="0.4"/>
    <material name="lens" rgba="0.02 0.02 0.03 1" specular="1" shininess="1"/>
    {cone_asset}
  </asset>
  <default>
    <default class="wheel">
      <!-- Ellipsoid wheels give a single smooth contact point. (The car once bounced
           off the floor; the cause was the drive gain kv=5, not the wheel shape.) -->
      <geom type="ellipsoid" size="{WHEEL_R} {WHEEL_W / 2} {WHEEL_R}" friction="{wheel_fric}"
            condim="4" contype="1" conaffinity="1" rgba="0 0 0 0"/>
    </default>
    <!-- Visual-only geoms: no contacts, zero density (no mass or inertia), so the
         calibrated physics is unchanged. -->
    <default class="vis">
      <geom contype="0" conaffinity="0" density="0" group="1"/>
      <default class="tyre"><geom type="cylinder" size="{WHEEL_R} {WHEEL_W / 2}" euler="1.5708 0 0" material="tyre"/></default>
      <default class="rim"><geom type="cylinder" size="{WHEEL_R * 0.62:.4f} {WHEEL_W / 2 + 0.0008:.4f}" euler="1.5708 0 0" material="rim"/></default>
      <default class="spoke"><geom type="box" size="{WHEEL_R * 0.6:.4f} {WHEEL_W / 2 + 0.0012:.4f} 0.0025" material="carbon"/></default>
    </default>
    <default class="cone"><geom contype="3" conaffinity="3" friction="0.8 0.01 0.0001"/></default>
  </default>
  <worldbody>
    <light directional="true" pos="0 0 10" dir="-0.35 0.25 -1" diffuse="0.75 0.75 0.72" specular="0.2 0.2 0.2" castshadow="true"/>
    <light directional="true" pos="0 0 10" dir="0.4 -0.3 -1" diffuse="0.2 0.2 0.22" castshadow="false"/>
    <geom name="floor" type="plane" size="60 60 0.1" material="floor" friction="1.0 0.01 0.0001" contype="1" conaffinity="1"/>
    <body name="car" pos="0 0 0.006">
      <freejoint name="car_free"/>
      <geom name="chassis" type="box" size="0.2 0.1 0.02" pos="0 0 0.037" mass="4.0" contype="2" conaffinity="2" rgba="0 0 0 0"/>
      <!-- Visual body (geometry only; the chassis box above carries mass and contacts) -->
      <geom class="vis" name="plate" type="box" size="0.2 0.072 0.004" pos="0 0 0.027" material="carbon"/>
      <geom class="vis" name="shell" type="ellipsoid" size="0.175 0.088 0.034" pos="0.005 0 0.058" material="body"/>
      <geom class="vis" name="stripe_l" type="box" size="0.07 0.006 0.001" pos="0.01 0.022 0.0912" material="stripe"/>
      <geom class="vis" name="stripe_r" type="box" size="0.07 0.006 0.001" pos="0.01 -0.022 0.0912" material="stripe"/>
      <geom class="vis" name="canopy" type="ellipsoid" size="0.065 0.048 0.024" pos="-0.03 0 0.086" material="glass"/>
      <geom class="vis" name="nose" type="ellipsoid" size="0.04 0.07 0.014" pos="0.17 0 0.04" material="body"/>
      <geom class="vis" name="bumper" type="capsule" fromto="0.205 -0.065 0.03 0.205 0.065 0.03" size="0.008" material="carbon"/>
      <geom class="vis" name="diffuser" type="box" size="0.02 0.07 0.008" pos="-0.19 0 0.035" material="carbon"/>
      <geom class="vis" name="strut_l" type="box" size="0.006 0.003 0.024" pos="-0.17 0.05 0.11" material="carbon"/>
      <geom class="vis" name="strut_r" type="box" size="0.006 0.003 0.024" pos="-0.17 -0.05 0.11" material="carbon"/>
      <geom class="vis" name="wing" type="box" size="0.03 0.105 0.003" pos="-0.172 0 0.136" euler="0 0.12 0" material="body"/>
      <geom class="vis" name="endplate_l" type="box" size="0.032 0.002 0.014" pos="-0.172 0.106 0.13" material="carbon"/>
      <geom class="vis" name="endplate_r" type="box" size="0.032 0.002 0.014" pos="-0.172 -0.106 0.13" material="carbon"/>
      <!-- OAK-D Lite on a mast, lens at the oak_rgb camera (kept behind the camera's view) -->
      <geom class="vis" name="mast" type="cylinder" fromto="0.075 0 0.09 0.075 0 0.118" size="0.004" material="carbon"/>
      <geom class="vis" name="oak_body" type="box" size="0.0085 0.045 0.0135" pos="0.081 0 0.13" material="oak"/>
      <geom class="vis" name="oak_lens" type="cylinder" size="0.0045 0.001" pos="0.0905 0 0.131" euler="0 1.5708 0" material="lens"/>
      <geom class="vis" name="oak_lens_l" type="cylinder" size="0.0035 0.001" pos="0.0905 0.0375 0.131" euler="0 1.5708 0" material="lens"/>
      <geom class="vis" name="oak_lens_r" type="cylinder" size="0.0035 0.001" pos="0.0905 -0.0375 0.131" euler="0 1.5708 0" material="lens"/>
      <site name="base_link" pos="{REAR_AXLE_X} 0 0.037" size="0.01"/>
      <camera name="chase" mode="trackcom" pos="-0.9 0 0.38" xyaxes="0 -1 0 0.38 0 0.92"/>
      <camera name="side" mode="trackcom" pos="0.25 -0.75 0.22" xyaxes="0.95 0.31 0 -0.06 0.2 0.98"/>
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
