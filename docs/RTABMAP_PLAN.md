# Plan: replace ArUco localization with RTAB-Map SLAM

Written 2026-11-11 as a hand-off document. It assumes no memory of the session that
produced it. Start from `main` at or after commit `e6004cf`.

## Goal

The car localizes and builds its own map with RTAB-Map from the RGB-D camera, instead of
relying on hand-surveyed ArUco markers (`saurcon_perception/config/marker_map.csv`).

## Where things stand today

| Piece | State |
|---|---|
| OS / ROS | Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic. `scripts/setup.sh` installs everything. |
| RTAB-Map | Not installed. `ros-jazzy-rtabmap-ros` 0.23.13 is available from apt. |
| Camera (sim) | RGB-D, 640×400, 15 Hz, horizontal FOV 1.204 rad, depth 0.1–10 m, mounted 0.219 m ahead of and 0.05 m above the rear axle. |
| Camera topics | `/camera/image`, `/camera/depth_image`, `/camera/camera_info`, bridged by `src/middle_earth/config/bridge_config.yaml`. Depth is recorded but unused. |
| Image frame id | `rc_vehicle/camera_link/rgbd_camera` — not in the TF tree. No `<gz_frame_id>` in the model. |
| TF today | static `base_link→camera_link`, `base_link→imu_link`; `map→base_link` from `saurcon_nav` (ArUco-corrected). No `odom` frame. |
| Wheel odometry | `/saurcon/odom` (TwistStamped: speed in `linear.x`, steer angle in `angular.z`) from `sim_saurcon_rc`; the ESP32 publishes the same on the real car. Gazebo also publishes `/model/rc_ackermann_vehicle/odom`. |
| IMU | `/saurcon/imu`, 100 Hz. |
| Clock | `/clock` is bridged; sim nodes run with `use_sim_time`. |
| Dead reckoning quality | Wheel speed + gyro alone drifted about 0.4 m over a 48 m lap in sim. |
| Baseline to beat | ArUco + UKF: 0.05 m RMS position error, 0.19 m max, 1.4° RMS heading on the test lap. |
| Test harness | `scripts/sim_eval/` (see Phase 0). |

## Target architecture

```
wheel speed + gyro ──► saurcon_nav (dead reckoning) ──► TF odom→base_link, /saurcon/odom_nav
RGB + depth + camera_info ─┐
odom ──────────────────────┴► rtabmap (rtabmap_slam) ──► TF map→odom, /map, /rtabmap/localization_pose
```

- `saurcon_nav` stops owning `map→base_link`. It publishes smooth, drifting `odom→base_link`.
- RTAB-Map owns `map→odom` and corrects drift through loop closures.
- Anything that needs the car's pose in the map reads TF `map→base_link`.

Using wheel/gyro odometry rather than RTAB-Map's visual odometry is the recommended
starting point: it already works, costs nothing, and does not fail in the low-texture
views this low-mounted camera gets. Visual odometry is a fallback (Phase 5).

## Phases

### Phase 0 — keep the measuring stick

The scripted-lap harness is in `scripts/sim_eval/`, copied from a temporary folder:

- `runsim.sh <workspace> <outdir>` launches the full sim, a ground-truth bridge, the logger and the driver.
- `driver.py` drives one lap through `/joy`, steering on simulator ground truth.
- `logger.py` records ground truth, `/saurcon/nav_state`, ArUco fixes and camera frames.
- `analyze.py` computes error statistics and renders plots and a video.

They contain hardcoded paths to the old temporary folder and to `/home/wilson/Code/saurcon_ws`;
make them path-relative first. Then confirm the baseline numbers above still reproduce.

### Phase 1A — simulated OAK-D Lite device

Replace the generic `rgbd_camera` on the vehicle with a reusable Gazebo model that
reproduces what the real OAK-D Lite (through Luxonis' `depthai-ros` driver) gives ROS, so
that everything downstream is written once against the real interface.

1. **Collect the real interface first.** From Luxonis' documentation and the
   `depthai-ros` driver, write down for the OAK-D Lite: each stream's resolution, FOV and
   rate; the stereo baseline; depth range and encoding; IMU rates; and the exact topic
   names, message types and TF frame names the driver publishes. Put the table in this
   document. The values below are from memory and must be checked:
   - left/right mono: 640×480, global shutter, about 73° horizontal FOV, 7.5 cm baseline;
   - colour: higher resolution, about 69° horizontal FOV, normally published downscaled;
   - depth: computed on the device from the mono pair, published aligned to one stream,
     16-bit millimetres, useful from about 0.2 m to a few metres;
   - IMU: accelerometer and gyro (BMI270);
   - driver topics of the form `/oak/rgb/image_raw`, `/oak/rgb/camera_info`,
     `/oak/stereo/image_raw`, `/oak/stereo/camera_info`, `/oak/left|right/...`,
     `/oak/imu/data`, with `oak_*_camera_optical_frame` frames.
2. **Build the model** at `src/middle_earth/models/oak_d_lite/` (`model.sdf`,
   `model.config`): a body of the real dimensions and mass, with these sensors on links
   placed at the real lens positions:
   - a colour camera;
   - left and right mono cameras (greyscale), one baseline apart;
   - a depth camera at the position of the stream the real depth is aligned to, with the
     same resolution and FOV as that stream;
   - an IMU.
   Set `<gz_frame_id>` on each sensor to the frame name the real driver uses.
3. **Make the depth behave like passive stereo, not like an ideal sensor.** Clip to the
   real minimum and maximum range, and add noise that grows with distance (stereo depth
   error grows with range squared for a fixed baseline). If Gazebo's built-in noise is
   not enough, add a small ROS node that post-processes the depth image: range-dependent
   noise, invalid pixels (zero) beyond range and on low-texture surfaces. Record which
   real effects are not modelled.
4. **Add image and IMU noise** at realistic levels so features and inertial data are not
   unrealistically clean.
5. **Bridge with the real topic names and types.** Extend
   `src/middle_earth/config/bridge_config.yaml` so the simulated device appears on the
   same topics as the real driver, including camera_info for every stream. Convert depth
   to the driver's encoding if Gazebo's differs (Gazebo gives 32-bit float metres).
6. **Publish the same TF tree** as the driver (device base frame → each camera frame →
   each optical frame, plus the IMU frame), from a small launch file or URDF, and attach
   the device base frame to `base_link` at the real mounting position.
7. **Mount it on the car**: `<include>` the model in
   `models/rc_ackermann_vehicle/model.sdf` with a fixed joint in place of the current
   `camera_link` sensor, and keep the old topic names available (remap or second bridge
   entry) until the ArUco nodes are removed.
8. **Verify:**
   - `ros2 topic list`, `ros2 topic hz` and `ros2 topic info` match the table from step 1;
   - camera_info intrinsics match resolution and FOV, and the left/right camera_info
     encode the baseline;
   - the depth image registers with its aligned image (overlay in RViz) and reads the
     right distance to a wall at 0.5, 1, 2 and 4 m, with invalid pixels outside the range;
   - the IMU reads gravity on the correct axis and the right sign of yaw rate in a turn;
   - re-run the ArUco baseline lap on the new camera to confirm nothing else broke.
9. **Write down the differences** between the simulated and real device in the model's
   folder (for example: no auto-exposure, no rolling-shutter colour camera, no on-device
   neural network outputs, idealised stereo matching).

### Phase 1B — make the sensor data RTAB-Map-ready

With the simulated OAK-D Lite from Phase 1A in place, steps 1 and 2 below are satisfied
by that model's frame names and TF tree; use its topics in place of `/camera/...`.


1. Add `<gz_frame_id>camera_optical_frame</gz_frame_id>` to the `rgbd_camera` sensor in
   `src/middle_earth/models/rc_ackermann_vehicle/model.sdf` (check the depth image and
   camera_info pick it up too).
2. Publish static TF `camera_link→camera_optical_frame` with the optical rotation
   (roll −π/2, yaw −π/2) in `full_sim_saurcon.launch.py`.
3. Verify with `ros2 run tf2_ros tf2_echo base_link camera_optical_frame` and by viewing
   the depth cloud in RViz: the floor must be flat and below the camera.
4. Check `/camera/camera_info` intrinsics match fx ≈ 465.7, cx = 320, cy = 200.
5. Check depth encoding (`32FC1` metres expected) and that RGB, depth and camera_info
   stamps agree; if not, use `approx_sync`.

### Phase 2 — odometry frame from saurcon_nav

1. Add a dead-reckoning mode to `saurcon_nav` (parameter, e.g. `use_aruco:=false`): run the
   existing prediction step only, starting at the origin, no ArUco survey.
2. Publish `nav_msgs/Odometry` in frame `odom` with child `base_link`, with a covariance
   that is honest about drift, and broadcast TF `odom→base_link`.
3. Keep the ArUco path selectable until RTAB-Map beats the baseline.
4. Test: run the lap, confirm drift is about the 0.4 m seen before and the TF tree is
   `odom→base_link→{camera_link→camera_optical_frame, imu_link}`.

### Phase 3 — RTAB-Map in simulation (mapping)

1. Add `rtabmap_ros` to `scripts/setup.sh` / `package.xml` and install it.
2. New launch file (suggest `saurcon_nav/launch/rtabmap_sim.launch.py`) starting
   `rtabmap_slam/rtabmap` with:
   - remaps `rgb/image→/camera/image`, `depth/image→/camera/depth_image`,
     `rgb/camera_info→/camera/camera_info`, `odom→` the Phase 2 topic;
   - `frame_id: base_link`, `odom_frame_id: odom`, `map_frame_id: map`,
     `subscribe_depth: true`, `approx_sync` as found in Phase 1B, `use_sim_time: true`;
   - a fixed `database_path` under the workspace, and `--delete_db_on_start` for mapping runs.
3. Starting parameters to tune: `Reg/Force3DoF=true` (ground vehicle),
   `RGBD/NeighborLinkRefining=true`, `Grid/RangeMax≈5`, `Grid/MaxGroundHeight` /
   `Grid/MaxObstacleHeight` for a camera ~0.1 m off the floor, `Vis/MinInliers`,
   `Rtabmap/DetectionRate≈2`.
4. Drive two laps with the harness. Success: a loop closure is accepted when the car
   returns to the start, and the occupancy grid shows the racks and walls in the right place.

Parameter and node names above are from memory of rtabmap_ros 0.21+; confirm them
against the installed version (`ros2 run rtabmap_slam rtabmap --params`) before relying on them.

### Phase 4 — localization mode and evaluation

1. Save the map database; relaunch with `Mem/IncrementalMemory=false` and
   `Mem/InitWMWithAllNodes=true` (localization only).
2. Extend `logger.py` to record TF `map→base_link` and `analyze.py` to score it.
   RTAB-Map's map origin is wherever mapping started, so align it to ground truth
   (start pose) before computing error.
3. Compare against the ArUco baseline on the same lap. Also test: starting somewhere
   other than the map origin, and a lap in the opposite direction.
4. ArUco is to be removed eventually, so also run the lap with the markers deleted from
   the world: the bare warehouse walls may not give enough features, and the OAK-D Lite's
   passive stereo needs texture for depth too.

### Phase 5 — fallbacks if Phase 3/4 struggle

- Too few visual features: raise camera resolution, add texture to the world, or enable
  RTAB-Map's own visual odometry (`rtabmap_odom/rgbd_odometry`) to compare.
- Odometry too poor on the real car: fuse wheel + IMU properly (keep the UKF, drop the
  ArUco update) or try `rgbd_odometry` with IMU as a guess.
- Loop closures wrong in the repetitive rack aisles: raise `Vis/MinInliers`, enable
  `RGBD/OptimizeMaxError`.

### Phase 6 — real vehicle (OAK-D Lite on a Raspberry Pi 4)

**Deferred:** all work is in simulation for now. Step 2 (make the simulator's camera match
the OAK-D Lite) is done early, as Phase 1A.

1. **Camera driver.** Use Luxonis' `depthai-ros` driver (check the Jazzy package name and
   that it builds on the Pi's arm64 Ubuntu 24.04). Configure it to publish depth aligned
   to one image stream, plus camera_info, at 640×400 or 640×480 and about 15 Hz to match
   the simulator. Compute stereo depth on the camera, not on the Pi.
2. **Make the simulator match.** Set the sim camera's resolution, FOV, rate and depth
   range to what the OAK-D Lite actually delivers, so tuning in sim carries over.
3. **TF.** Measure the real camera mounting and use the driver's optical frame names in
   place of `camera_optical_frame`.
4. **Pi 4 CPU budget.** Start with wheel/gyro odometry only (no visual odometry),
   `Rtabmap/DetectionRate` 1 Hz, image decimation, a coarse grid (`Grid/CellSize` 0.05),
   and `Mem/ImagePreDecimation`/feature limits (`Kp/MaxFeatures`, `Vis/MaxFeatures`)
   turned down. Measure CPU and memory before adding anything.
5. **If the Pi cannot keep up while mapping:** build the map with `rtabmap` running on
   the desktop over the network (the Pi only runs the camera and odometry), then copy the
   database to the Pi and run localization-only there, which is much lighter.
6. **Launch.** A vehicle launch file alongside `saurcon.launch.py` that adds the camera
   driver, the odometry node and RTAB-Map.
7. **Orin NX later.** The same launch should work; raise detection rate and resolution,
   and visual odometry becomes affordable.

### Phase 7 — retire ArUco

Once RTAB-Map meets the baseline: remove the ArUco nodes from `full_sim_saurcon.launch.py`,
the ArUco update from `saurcon_nav`, and the `saurcon_perception` package and marker models.
Update `README.md` and `BUGS.md`.

## Decisions (Wilson, 2026-11-11)

| Question | Answer | Consequence |
|---|---|---|
| Depth camera | Luxonis OAK-D Lite | Passive stereo depth computed on the camera; see hardware notes below. |
| Onboard computer | Raspberry Pi 4 for now, possibly an Orin NX later | RTAB-Map must be tuned down hard; wheel/gyro odometry rather than visual odometry; mapping may need to run off-board. |
| Output | 2-D occupancy grid as well as pose | Keep `Grid/*` parameters in scope from Phase 3; publish `/map` for Nav2 later. |
| Scope | Simulation only for now | Do Phases 0–5 and 7 in sim. Phase 6 (real vehicle) is deferred; Phase 1A builds a simulated OAK-D Lite so results carry over. |
| ArUco | Remove in future | Phase 7 deletes the ArUco nodes rather than keeping them as a fallback. |

### OAK-D Lite notes (from memory — verify against Luxonis' documentation)

- Stereo pair of global-shutter mono cameras at 640×480 with a 7.5 cm baseline, plus a
  higher-resolution colour camera. Depth is computed on the device.
- Passive stereo with no IR projector: depth is poor on blank walls and floors, so the
  environment needs visual texture. This matters for the decision to remove the markers.
- Useful depth range is roughly 0.2 m to a few metres with a 7.5 cm baseline; treat the
  simulator's 10 m range as optimistic and cap `Grid/RangeMax` around 3–4 m.
- This unit has an onboard IMU (confirmed by Wilson). It is rigidly attached to the
  camera, so it is a candidate for visual-inertial odometry later; the car's own IMU is
  already on `/saurcon/imu`.
- Needs a USB 3 port and a good power supply on the Pi 4.

## Still open

- **Was there an earlier Copilot RTAB-Map attempt?** It is not on GitHub in this
  repository (checked all four branches on 2026-11-11); it may be unpushed on the
  `wilson-desktop` machine.

## Risks

- The camera sits about 9 cm above the floor, so much of the image is floor; features and
  depth are concentrated in the top half.
- The warehouse aisles look alike, which invites false loop closures.
- Sim depth is perfect; real depth cameras are noisy beyond a few metres and have a
  minimum range.
- RTAB-Map publishes `map→odom` at its detection rate with jumps on loop closure; any
  controller should follow `odom`-frame motion and treat `map` corrections as slow.

## Practical notes for whoever picks this up

- `sudo` needs a password. For unattended installs, run with
  `SUDO_ASKPASS=<script calling zenity --password>` so the user types it into a dialog.
- No gamepad is attached to this machine; `/dev/input/js0` is a keyboard. Drive with
  `scripts/sim_eval/driver.py` or `src/middle_earth/scripts/teleop_vehicle.py`.
- The launch file opens the Gazebo GUI. For headless tests use
  `gz sim -s -r --headless-rendering <world>` with `GZ_SIM_RESOURCE_PATH` set to
  `src/middle_earth/models:src/middle_earth`.
- Kill leftover nodes between runs. Process names are truncated to 15 characters
  (`state_estimator`, `parameter_bridg`), and `pkill -f` patterns can match the shell
  running them.
- The simulator's true pose is on Gazebo topic
  `/world/warehouse_racetrack/dynamic_pose/info`; the first entry is the vehicle model,
  whose origin is 0.127 m ahead of `base_link`.
- `gh` is not installed.

## Implementation interface (2026-11-12)

The selected simulation stream table, verified source links and explicit
approximations are in
[`oak_d_lite/README.md`](../src/middle_earth/models/oak_d_lite/README.md).
It distinguishes configurable output choices from hardware capabilities. In
particular RGB is kept at the legacy 640×400 calibration for baseline comparison;
IMU extrinsics are assumed pending real-device calibration. Do not treat this
model as a fully calibrated replica. See `RTABMAP_STATUS.md` for measured results.

### Selected ROS interface

| ROS topic | Type / encoding | Profile | Frame |
|---|---|---|---|
| `/oak/rgb/image_raw` | sensor_msgs/Image, rgb8 | 640×400, 15 Hz, 1.204 rad horizontal FOV | oak_rgb_camera_optical_frame |
| `/oak/rgb/camera_info` | sensor_msgs/CameraInfo | fx=fy≈465.74; cx=320, cy=200 | same |
| `/oak/stereo/image_raw` | sensor_msgs/Image, 16UC1 millimetres, zero invalid | RGB-aligned, 640×400, 15 Hz, accepted range 0.2–4 m | same |
| `/oak/stereo/camera_info` | sensor_msgs/CameraInfo | RGB intrinsics | same |
| `/oak/left/image_raw`, `/oak/right/image_raw` | sensor_msgs/Image, mono8 | 640×480, 15 Hz, 73° horizontal FOV | oak_left/right_camera_optical_frame |
| `/oak/left/camera_info`, `/oak/right/camera_info` | sensor_msgs/CameraInfo | 75 mm baseline; right P[3] = −fx×0.075 | same |
| `/oak/imu/data` | sensor_msgs/Imu | 100 Hz | oak_imu_frame |

These are the selected simulation profile values, not fixed factory defaults.
See the linked model README for hardware limits, primary sources, rate/crop
choices, noise assumptions and the uncalibrated IMU-extrinsic limitation.
