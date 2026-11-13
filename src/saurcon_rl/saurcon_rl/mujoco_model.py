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
        <geom class="tyre"/><geom class="rim"/><geom class="spoke"/><geom class="spoke" euler="0 1.0472 0"/><geom class="spoke" euler="0 2.0944 0"/><geom class="hub"/>
      </body>''' for side, y in (('left', TRACK / 2), ('right', -TRACK / 2)))
    front = ''.join(f'''
      <body name="{side}_knuckle" pos="{-REAR_AXLE_X} {y:.5f} {0.04 - 0.003:.4f}">
        <joint name="{side}_steer" type="hinge" axis="0 0 1" range="{-STEER_JOINT_LIMIT} {STEER_JOINT_LIMIT}" damping="{steer_damping}"/>
        <geom type="sphere" size="0.008" mass="0.1" contype="0" conaffinity="0" rgba="0.92 0.92 0.9 1"/>
        <geom class="vis" type="box" size="0.009 0.006 0.016" pos="0 {-0.024 if y > 0 else 0.024:.3f} -0.01" material="pla"/>
        <body name="{side}_front_wheel" pos="0 0 -0.01">
          <joint name="{side}_front_spin" type="hinge" axis="0 1 0" damping="0.0001"/>
          <geom class="wheel" mass="0.3"/>
          <geom class="tyre"/><geom class="rim"/><geom class="spoke"/><geom class="spoke" euler="0 1.0472 0"/><geom class="spoke" euler="0 2.0944 0"/><geom class="hub"/>
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
    <!-- Visual-only car materials, after the real car (photos 2026-11-13): white 3D-printed
         chassis and decks, red printed front bumper, green bracket, MG90S servo, OAK-D Lite in a
         white cradle, black tyres on black rims. The red bumper is cone-coloured but sits well
         below the OAK camera's field of view (checked: nothing of the car is in its image). -->
    <material name="pla" rgba="0.92 0.92 0.9 1" specular="0.25" shininess="0.3"/>
    <material name="red" rgba="0.93 0.13 0.07 1" specular="0.4" shininess="0.5"/>
    <material name="green" rgba="0.16 0.62 0.32 1" specular="0.3"/>
    <material name="carbon" rgba="0.07 0.07 0.08 1" specular="0.3" shininess="0.3"/>
    <material name="servo" rgba="0.05 0.05 0.06 1" specular="0.6" shininess="0.6"/>
    <material name="label" rgba="0.86 0.2 0.55 1" specular="0.6"/>
    <material name="battery" rgba="0.72 0.74 0.76 1" specular="0.8" shininess="0.7"/>
    <material name="tyre" rgba="0.04 0.04 0.04 1" specular="0.05"/>
    <material name="rim" rgba="0.1 0.1 0.11 1" specular="0.6" shininess="0.6"/>
    <material name="hub" rgba="0.55 0.55 0.58 1" specular="0.9" shininess="0.9"/>
    <material name="oak" rgba="0.12 0.12 0.13 1" specular="0.4"/>
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
      <default class="rim"><geom type="cylinder" size="{WHEEL_R * 0.66:.4f} {WHEEL_W / 2 + 0.0008:.4f}" euler="1.5708 0 0" material="rim"/></default>
      <default class="spoke"><geom type="box" size="{WHEEL_R * 0.64:.4f} {WHEEL_W / 2 + 0.0012:.4f} 0.0018" material="tyre"/></default>
      <default class="hub"><geom type="cylinder" size="0.006 {WHEEL_W / 2 + 0.0016:.4f}" euler="1.5708 0 0" material="hub"/></default>
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
      <!-- Visual body (geometry only; the chassis box above carries mass and contacts).
           Chassis frame: x forward from mid-wheelbase, axles at x = -/+0.127. -->
      <!-- lower tray with the battery pack, open sides -->
      <geom class="vis" name="tray_floor" type="box" size="0.15 0.046 0.003" pos="-0.02 0 0.024" material="pla"/>
      <geom class="vis" name="tray_rail_l" type="box" size="0.15 0.003 0.004" pos="-0.02 0.046 0.03" material="pla"/>
      <geom class="vis" name="tray_rail_r" type="box" size="0.15 0.003 0.004" pos="-0.02 -0.046 0.03" material="pla"/>
      <geom class="vis" name="tray_top_l" type="box" size="0.15 0.003 0.003" pos="-0.02 0.046 0.058" material="pla"/>
      <geom class="vis" name="tray_top_r" type="box" size="0.15 0.003 0.003" pos="-0.02 -0.046 0.058" material="pla"/>
      <geom class="vis" name="tray_post_fl" type="box" size="0.006 0.003 0.014" pos="0.06 0.046 0.044" material="pla"/>
      <geom class="vis" name="tray_post_fr" type="box" size="0.006 0.003 0.014" pos="0.06 -0.046 0.044" material="pla"/>
      <geom class="vis" name="tray_post_rl" type="box" size="0.006 0.003 0.014" pos="-0.1 0.046 0.044" material="pla"/>
      <geom class="vis" name="tray_post_rr" type="box" size="0.006 0.003 0.014" pos="-0.1 -0.046 0.044" material="pla"/>
      <geom class="vis" name="battery" type="box" size="0.07 0.036 0.016" pos="-0.02 0 0.043" material="battery"/>
      <geom class="vis" name="battery_label" type="box" size="0.04 0.0365 0.008" pos="-0.03 0 0.043" material="carbon"/>
      <!-- upper deck on standoffs -->
      <geom class="vis" name="deck" type="box" size="0.12 0.05 0.003" pos="-0.03 0 0.075" material="pla"/>
      <geom class="vis" name="deck_rail_l" type="box" size="0.12 0.004 0.006" pos="-0.03 0.05 0.081" material="pla"/>
      <geom class="vis" name="deck_rail_r" type="box" size="0.12 0.004 0.006" pos="-0.03 -0.05 0.081" material="pla"/>
      <geom class="vis" name="post_fl" type="cylinder" fromto="0.07 0.04 0.026 0.07 0.04 0.072" size="0.0025" material="carbon"/>
      <geom class="vis" name="post_fr" type="cylinder" fromto="0.07 -0.04 0.026 0.07 -0.04 0.072" size="0.0025" material="carbon"/>
      <geom class="vis" name="post_rl" type="cylinder" fromto="-0.13 0.04 0.026 -0.13 0.04 0.072" size="0.0025" material="carbon"/>
      <geom class="vis" name="post_rr" type="cylinder" fromto="-0.13 -0.04 0.026 -0.13 -0.04 0.072" size="0.0025" material="carbon"/>
      <!-- computer box with the green bracket, behind the camera -->
      <geom class="vis" name="pi_case" type="box" size="0.06 0.042 0.016" pos="-0.04 0 0.095" material="pla"/>
      <geom class="vis" name="bracket" type="box" size="0.035 0.044 0.004" pos="0.005 0 0.082" material="green"/>
      <geom class="vis" name="bracket_tab" type="box" size="0.012 0.004 0.012" pos="0.02 -0.046 0.09" material="green"/>
      <!-- OAK-D Lite (91 x 28 x 17.5 mm) in a white cradle on a stand; lens at the oak_rgb camera -->
      <geom class="vis" name="oak_stand" type="box" size="0.012 0.022 0.012" pos="0.072 0 0.093" material="pla"/>
      <geom class="vis" name="cradle" type="box" size="0.012 0.052 0.0175" pos="0.0765 0 0.131" material="pla"/>
      <geom class="vis" name="oak_body" type="box" size="0.0035 0.0455 0.014" pos="0.0865 0 0.131" material="oak"/>
      <geom class="vis" name="oak_lens" type="cylinder" size="0.0045 0.001" pos="0.0905 0 0.131" euler="0 1.5708 0" material="lens"/>
      <geom class="vis" name="oak_lens_l" type="cylinder" size="0.0035 0.001" pos="0.0905 0.0375 0.131" euler="0 1.5708 0" material="lens"/>
      <geom class="vis" name="oak_lens_r" type="cylinder" size="0.0035 0.001" pos="0.0905 -0.0375 0.131" euler="0 1.5708 0" material="lens"/>
      <!-- front end: crossmember, wishbones, MG90S servo, red truss bumper -->
      <geom class="vis" name="front_plate" type="box" size="0.03 0.03 0.004" pos="0.125 0 0.034" material="pla"/>
      <geom class="vis" name="arm_fl" type="capsule" fromto="0.105 0.022 0.045 0.127 0.058 0.04" size="0.0035" material="pla"/>
      <geom class="vis" name="arm_rl" type="capsule" fromto="0.15 0.022 0.045 0.127 0.058 0.04" size="0.0035" material="pla"/>
      <geom class="vis" name="arm_fr" type="capsule" fromto="0.105 -0.022 0.045 0.127 -0.058 0.04" size="0.0035" material="pla"/>
      <geom class="vis" name="arm_rr" type="capsule" fromto="0.15 -0.022 0.045 0.127 -0.058 0.04" size="0.0035" material="pla"/>
      <geom class="vis" name="link_l" type="capsule" fromto="0.115 0.006 0.052 0.115 0.055 0.05" size="0.0022" material="pla"/>
      <geom class="vis" name="link_r" type="capsule" fromto="0.115 -0.006 0.052 0.115 -0.055 0.05" size="0.0022" material="pla"/>
      <geom class="vis" name="servo" type="box" size="0.006 0.0115 0.0145" pos="0.122 0 0.06" material="servo"/>
      <geom class="vis" name="servo_label" type="box" size="0.0005 0.009 0.006" pos="0.1282 0 0.063" material="label"/>
      <geom class="vis" name="servo_horn" type="box" size="0.004 0.009 0.0015" pos="0.118 0 0.0475" material="pla"/>
      <geom class="vis" name="bumper_bar" type="box" size="0.006 0.088 0.007" pos="0.212 0 0.022" material="red"/>
      <geom class="vis" name="bumper_strut_l" type="box" size="0.034 0.004 0.006" pos="0.18 0.04 0.022" euler="0 0 -0.85" material="red"/>
      <geom class="vis" name="bumper_strut_r" type="box" size="0.034 0.004 0.006" pos="0.18 -0.04 0.022" euler="0 0 0.85" material="red"/>
      <geom class="vis" name="bumper_spine" type="box" size="0.03 0.005 0.006" pos="0.18 0 0.022" material="red"/>
      <geom class="vis" name="bumper_tip_l" type="box" size="0.004 0.004 0.006" pos="0.206 0.09 0.022" material="red"/>
      <geom class="vis" name="bumper_tip_r" type="box" size="0.004 0.004 0.006" pos="0.206 -0.09 0.022" material="red"/>
      <!-- rear axle -->
      <geom class="vis" name="rear_axle" type="cylinder" fromto="-0.127 0.07 0.03 -0.127 -0.07 0.03" size="0.003" material="hub"/>
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
