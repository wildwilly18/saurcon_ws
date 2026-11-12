# Known bugs and issues

Review of the whole workspace on 2026-11-11 (ROS 2 Jazzy, Gazebo Harmonic, Ubuntu 24.04).
Items are ordered by severity within each section. "Confirmed" means the behaviour was
reproduced in the simulator or in existing data; everything else was found by reading the code.

The submodules (`micro-ROS-Agent`, `micro_ros_msgs`) were not reviewed.

## Status (2026-11-11)

All items below have been addressed in the working tree (uncommitted). Two more
issues (26, 27) were found while verifying the fixes in the simulator and are fixed too.

Verification, same scripted lap of the racetrack (46 s at 1 m/s, steering closed-loop on
simulator ground truth, driven through the normal `/joy` interface):

| | Position error RMS | Position error max | Heading error RMS |
|---|---|---|---|
| Original code | 0.23 m | 0.43 m | 2.0° |
| Fixed code | 0.05 m | 0.19 m | 1.4° |

Joystick-loss test at the end of the lap (controller goes silent with throttle applied):
the original code kept driving at the last command; the fixed code enters FAULT, stops,
and returns to STANDBY when the view button is held.

Not tested: anything on the real vehicle (micro-ROS agent launches, real IMU/camera),
and a real gamepad (the joystick was simulated by publishing `/joy`).

## Summary

| # | Severity | Area | Issue | Status |
|---|----------|------|-------|--------|
| 1 | High | perception | Markers 3 and 10 face the wrong way in the marker map (confirmed) | Fixed |
| 2 | High | rc | Joystick loss in RUN_CONTROL keeps driving at the last command | Fixed |
| 3 | High | nav | Estimator can permanently reject all ArUco fixes | Fixed |
| 4 | High | rc | State machine reads uninitialised members | Fixed |
| 5 | Medium | nav | Gyro bias is divided by the wrong sample count | Fixed |
| 6 | Medium | rc | Joystick axes/buttons indexed without bounds checks | Fixed |
| 7 | Medium | nav | Fixed wall-clock `dt` and mixed time bases | Fixed |
| 8 | Medium | nav | No guard against a non-positive-definite covariance / NaN state | Fixed |
| 9 | Medium | nav | Only one ArUco fix per frame is used | Fixed |
| 10 | Medium | perception | Launch parameters and remaps are silently ignored | Fixed |
| 11 | Medium | sim | `start_simulation.sh` / `bridge_config.yaml` bridge topics that do not exist | Fixed |
| 12 | Medium | scripts | `extract_rosbag.py` writes malformed CSVs (confirmed) | Fixed |
| 13 | Medium | rc | FAULT state is a dead end and its handler is never called | Fixed, except RUN_AUTONOMOUS is still unreachable (no autonomous controller exists yet) |
| 14 | Low | rc | Vehicle can keep its last velocity when leaving RUN_CONTROL in sim | Fixed |
| 15 | Low | nav | Last survey measurement is applied twice | Fixed |
| 16 | Low | nav | Zero-velocity bypass ignores rotation and needs exactly 0.0 | Fixed |
| 17 | Low | nav | Output frame, validity and documentation mismatches | Fixed |
| 18 | Low | perception | `camera_params.json` intrinsics are inconsistent; rotation unused | Fixed |
| 19 | Low | perception | Marker-map parsing can crash on a malformed row | Fixed |
| 20 | Low | perception | Wasted work per frame in the detector | Fixed |
| 21 | Low | build | Build writes tracked `.exe` files into the source tree (confirmed) | Fixed |
| 22 | Low | sim | ROS 1 leftovers in `middle_earth` | Fixed |
| 23 | Low | sim | Vehicle geometry mismatch in the Ackermann plugin | Fixed |
| 24 | Low | launch | Launch-file rough edges | Fixed; the `bringup` / `saurcon_main` overlap is documented in the launch file, not prevented |
| 25 | Low | repo | Build artefacts and stale docs are tracked | Fixed |
| 26 | High | sim / perception | Markers rendered too dark and with the wrong size; detector locked onto the plate edge | Fixed |
| 27 | High | perception / nav | Ambiguous and distant marker poses fed to the filter with fixed 0.1 m noise | Fixed |

Already fixed during setup (uncommitted): hardcoded `/home/wilson-desktop` and
`/home/wilson/saurcon_ws` paths, the wrong executable name in `aruco_detector.launch.py`,
missing `package.xml` dependencies, and the `<odometry_topic>` tag in the vehicle model
(Gazebo expects `<odom_topic>`, so odometry was published on `/model/rc_vehicle/odometry`).

---

## High

### 1. Markers 3 and 10 face the wrong way in the marker map (confirmed)

- **Where:** `src/saurcon_perception/config/marker_map.csv` (ids 3 and 10); same values in
  `src/middle_earth/worlds/tag_locations.csv`.
- **What:** the map gives marker 3 `psi = +1.5708` and marker 10 `psi = -1.5708`. In
  `racetrack.world` the white backing plates put the visible face of marker 3 on its −Y side
  and of marker 10 on its +Y side, i.e. the opposite of the map.
- **Effect:** when the car sees either end-of-track marker, the localizer places it mirrored
  through the marker, about 3.6 m off with heading reversed.
- **Evidence:** vehicle teleported in front of each marker, headless sim:

  | Marker | True pose (x, y, yaw) | Localizer output |
  |--------|-----------------------|------------------|
  | 0 | −1.13, 0.00, 0.00 | −1.13, 0.00, 0.00 |
  | 3 | 9.0, ≈0.4, +1.57 | 9.0, 4.0, −1.57 |
  | 10 | −12.5, ≈3.6, −1.57 | −12.5, 0.0, +1.57 |
  | 12 | −8.6…−8.9, 0.0, 0.00 | −8.7…−8.9, 0.0, 0.00 |
  | 5 | 5.1…5.4, 4.0, 3.14 | 5.2…5.4, 4.0, 3.14 |

- **Fix:** set marker 3 to `psi = -1.5708` and marker 10 to `psi = 1.5708` in both CSVs.
- **Related:** markers 11–13 have yaw `0` in the world but `3.14159` in the map. That works
  only because the camera sees the back face of the box. Making the world yaw match the map
  (and moving the backing plates) would remove the trap.

### 2. Joystick loss in RUN_CONTROL keeps driving at the last command

- **Where:** `src/saurcon_rc/src/state_machine.cpp`, `handle_RUN_CONTROL()` — the
  `check_heartbeat()` call is commented out.
- **What:** `joy_msg` holds the last received stick values and is copied to `/ctrl_output`
  every 30 ms. Nothing checks that `/joy` or `/saurcon/state` are still arriving.
- **Effect:** if the controller disconnects or `joy_node` dies while the throttle is held, the
  vehicle keeps driving at that throttle indefinitely.
- **Fix:** re-enable the heartbeat check. Before doing so, initialise `last_rc_heartbeat_` and
  `last_ctrl_heartbeat_` with `this->now()` in the constructor: a default-constructed
  `rclcpp::Time` uses a different clock type, and subtracting it from `now()` throws.

### 3. Estimator can permanently reject all ArUco fixes

- **Where:** `src/saurcon_nav/src/state_estimator.cpp`, `measurementUpdate()` (10-sigma
  Mahalanobis gate) together with `initializeQ()` and the SURVEY timeout branch.
- **What:** `Q` has no X/Y terms, so position covariance barely grows. With the initial
  0.2 m standard deviation and the 0.1 m measurement noise, the gate is roughly 2.2 m.
- **Effect:**
  - If no marker is seen within 5 s, the filter initialises at (0, 0, 0). Any later fix more
    than ~2 m from the origin is rejected, and so is every fix after it.
  - The same lock-out happens after enough dead-reckoning drift, or after one bad fix such as
    issue 1.
- **Fix:** add X/Y process noise scaled by speed; on timeout start with a large covariance
  rather than 0.2 m; re-initialise from ArUco after N consecutive rejections.

### 4. State machine reads uninitialised members

- **Where:** `src/saurcon_rc/include/saurcon_rc/state_machine.hpp` — `menu_held`,
  `view_held`, `menu_transition_triggered`, `view_transition_triggered`, `throttle`, `steer`,
  `saurcon_rc_desired_state_` have no initialisers.
- **What:** `handle_STANDBY()` reads `menu_held` every 30 ms, before any `/joy` message has
  set it.
- **Effect:** undefined behaviour. If `menu_held` happens to be non-zero, the node either
  throws on the time subtraction (see issue 2) or jumps to RUN_CONTROL with no button press.
- **Fix:** give every member a default (`bool menu_held{false};` etc.).

---

## Medium

### 5. Gyro bias is divided by the wrong sample count

- **Where:** `state_estimator.cpp`, `initializeIMU()`.
- **What:** 100 samples are summed, but the sum is divided by `imu_counts` (all IMU messages
  received so far) instead of the number of samples. The log from a sim run shows
  `imu_counts=199` at that point.
- **Effect:** the bias estimate is about half the true value. Invisible in simulation (zero
  bias) but will cause heading drift on the real IMU.
- **Fix:** divide by `gz_readings.size()`. Also consider checking that the vehicle is
  stationary during the survey.
- **Minor:** `imu_last_seq` is `uint16_t` while `seq` is `size_t`.

### 6. Joystick axes/buttons indexed without bounds checks

- **Where:** `state_machine.cpp` `control_input_cb()`; `src/saurcon_rc/src/ctrl_interface.cpp`
  `joy_callback()`; `src/saurcon_rc/src/sim_saurcon_rc.cpp` `joint_state_cb()`
  (`velocity[]` / `position[]`).
- **What:** `axes[1]`, `axes[3]`, `buttons[6]`, `buttons[7]` are read without checking sizes.
- **Effect:** out-of-bounds read with any device that reports fewer axes or buttons. The
  indices also assume the wired Xbox (`xpad`) layout seen in `test_bags`; Bluetooth or other
  pads map differently.
- **Fix:** check sizes and return early; make the indices parameters.

### 7. Fixed wall-clock `dt` and mixed time bases

- **Where:** `src/saurcon_nav/src/state_estimator_node.cpp` (`dt_ = 0.02`, wall timer);
  `sim_saurcon_rc.cpp` (`imu_data_cb`, `publish_rc_odom` stamp with `now()`).
- **What:**
  - The filter integrates with a constant 20 ms regardless of how much time actually passed.
  - IMU and odometry are re-stamped with wall time, while ArUco fixes carry the camera's
    simulation time (seconds since sim start). No node sets `use_sim_time`.
  - Only the newest IMU sample is used each cycle, so half of the 100 Hz samples are dropped.
- **Effect:** dead reckoning is scaled wrong whenever the simulator runs slower or faster than
  real time or the timer jitters. Timestamps from different sensors cannot be compared.
- **Fix:** compute `dt` from message stamps, use one time base (set `use_sim_time` and bridge
  `/clock` in sim), and integrate all IMU samples between updates.

### 8. No guard against a non-positive-definite covariance / NaN state

- **Where:** `state_estimator.cpp`, `generateSigmaPoints()` and `measurementUpdate()`.
- **What:** `llt()` results are used without checking `info()`. The update
  `P = P⁻ − K S Kᵀ` and the negative centre weight (`alpha = 0.1` gives `Wc₀ ≈ −96`) can both
  produce a covariance that is not positive definite. While stationary, repeated updates with
  no process noise also shrink `P` towards zero.
- **Effect:** one failed decomposition yields NaNs that propagate into the state and never
  clear.
- **Fix:** check `llt().info()`, symmetrise `P` and add a small floor to its diagonal, and
  reset the filter if the state is not finite.

### 9. Only one ArUco fix per frame is used

- **Where:** `state_estimator.cpp` `measurementUpdate()`; `aruco_localizer_node.cpp`
  `detectionCb()`.
- **What:** the localizer publishes one message per visible marker, all with the same stamp.
  The estimator reads only `localization_buffer.front()` once per 50 Hz cycle and treats a
  fix as fresh only if its stamp is strictly newer.
- **Effect:** when two markers are visible, one of the two fixes is always discarded.
- **Fix:** process every unprocessed buffer entry (track by `seq`, not timestamp).

### 10. Launch parameters and remaps are silently ignored

- **Where:** `src/saurcon_rc/launch/full_sim_saurcon.launch.py`,
  `src/saurcon_perception/launch/aruco_detector.launch.py`,
  `src/saurcon_perception/config/aruco_params.yaml`.
- **What:** the launch files set `marker_size`, `dictionary_id`, `camera_frame`,
  `publish_visualization`, `min_marker_id`, `max_marker_id` and remap `image_raw`,
  `camera_info`, `odom`. The nodes declare none of these; they read `camera_topic`,
  `aruco_topic`, and the JSON/CSV files in `config/`.
- **Effect:** changing the marker size or image topic in a launch file does nothing. The
  standalone detector launch defaults to `/camera/image_raw` but the node still subscribes to
  `/camera/image`. `/camera/camera_info` is never bridged.
- **Fix:** either declare and use these parameters in the nodes, or delete them from the
  launch files and `aruco_params.yaml`.

### 11. `start_simulation.sh` / `bridge_config.yaml` bridge topics that do not exist

- **Where:** `src/middle_earth/config/bridge_config.yaml`,
  `src/middle_earth/scripts/start_simulation.sh`, `start_bridge.sh`.
- **What:** the config bridges Gazebo `/cmd_vel` and `/imu`. The vehicle model uses
  `/model/rc_ackermann_vehicle/cmd_vel` and `/model/rc_ackermann_vehicle/imu`.
- **Effect:** the script starts Gazebo and a bridge, but the suggested
  `ros2 topic pub /cmd_vel ...` never reaches the vehicle and no IMU data arrives.
- **Fix:** update the Gazebo topic names in `bridge_config.yaml`. The six separate bridge
  processes in `full_sim_saurcon.launch.py` could then use this one file too, which also
  removes the duplicate `ros_gz_bridge` node-name warning.
- **Also:** `start_simulation.sh` runs `killall -9 gz` / `pkill -9 gz`, which kills any other
  Gazebo session on the machine.

### 12. `extract_rosbag.py` writes malformed CSVs (confirmed)

- **Where:** `scripts/extract_rosbag.py`, `get_message_fields()` / `extract_message_data()`.
- **What:**
  - Primitive arrays arrive as `array.array`, which the `isinstance(..., (list, tuple,
    np.ndarray))` check misses. They are written as one cell, e.g.
    `"array('d', [0.0, 0.0, ...])"` — visible in `test_bags/.../joy.csv` and
    `..._joint_states.csv`.
  - The header is built from the first message only. Topics with variable-length arrays
    (`/aruco_poses`) get rows whose column count differs from the header.
- **Fix:** include `array.array` in the type check; for variable-length fields write a count
  plus a JSON cell, or one row per element.

### 13. FAULT state is a dead end and its handler is never called

- **Where:** `state_machine.cpp`, `handleCurrentState()` (`case FAULT: break;`).
- **What:** `handle_FAULT()` exists but is not called, and there is no transition out of
  FAULT. RUN_AUTONOMOUS is also unreachable: the comment in `handle_STANDBY()` says the view
  button should enter it, but only the menu button is handled.
- **Effect:** once the heartbeat check (issue 2) is enabled, any fault needs a node restart.
- **Fix:** call the handler and add a recovery path (for example, hold view to return to
  STANDBY).

---

## Low

### 14. Vehicle can keep its last velocity when leaving RUN_CONTROL in sim

- **Where:** `sim_saurcon_rc.cpp`, `ctrl_output_cb()` / `state_cmd_cb()`.
- **What:** commands are forwarded to Gazebo only in RUN states, and no zero command is sent
  on the transition out. Stopping relies on a stop message arriving in the gap before the
  1 Hz `/rc_state_cmd` publish.
- **Fix:** publish a zero `Twist` in `state_cmd_cb()` when leaving a RUN state; publish
  `/rc_state_cmd` immediately on state change rather than waiting for the 1 Hz timer.

### 15. Last survey measurement is applied twice

- **Where:** `state_estimator.cpp`, `initializeStart()`.
- **What:** `last_localization_time` is not updated during SURVEY, so the first NAVIGATE cycle
  treats the final survey fix as new and applies it again.
- **Fix:** set `last_localization_time = meas.time_stamp` in `initializeStart()`.

### 16. Zero-velocity bypass ignores rotation and needs exactly 0.0

- **Where:** `state_estimator.cpp`, NAVIGATE branch (`std::abs(v_b) <= 1e-9`).
- **What:** prediction is skipped only when odometry is exactly zero, which real encoders
  rarely report. When it is skipped, gyro rotation is ignored too.
- **Fix:** use a small speed threshold and still integrate heading.

### 17. Output frame, validity and documentation mismatches

- **Where:** `state_estimator_node.cpp`, `state_estimator.hpp`.
- **What:**
  - `/saurcon/nav_state` is stamped `frame_id = "odom"` but the pose is in the marker-map
    frame (`"map"` in the localizer).
  - It is published with zeros during STARTUP/SURVEY, with no flag that it is not yet valid.
  - The header comment says odometry is a measurement of V; the code uses it as a control
    input, so the V state is simply overwritten each step.
  - No TF is broadcast.

### 18. `camera_params.json` intrinsics are inconsistent; rotation unused

- **Where:** `src/saurcon_perception/config/camera_params.json`,
  `src/saurcon_perception/src/aruco_detector.cpp`.
- **What:** `focal_length_x/y = 929.4` does not match 640 px at 1.204 rad (≈ 466 px). It is
  harmless today because the FOV takes precedence, but it will be wrong if the FOV is removed
  for a real camera. `rotation.roll/pitch/yaw` are loaded and never applied, distortion is
  always zero, and the detector's `T_vc_` is computed but unused.

### 19. Marker-map parsing can crash on a malformed row

- **Where:** `src/saurcon_perception/src/aruco_localizer_node.cpp`, `loadMarkerMap()`.
- **What:** `std::stoi` / `std::stod` are not wrapped, so a non-numeric cell throws and the
  node exits at startup. (The detector's whitelist loader does catch this.)

### 20. Wasted work per frame in the detector

- **Where:** `aruco_detector.cpp`, `getTagsInImage()`.
- **What:** a debug image is converted and drawn on every frame and then discarded; the CLAHE
  object and detector parameters are rebuilt per frame. The camera publishes at 15 Hz but the
  pipeline was measured at about 12 Hz.
- **Also:** `solvePnP` is called with the default solver; `SOLVEPNP_IPPE_SQUARE` is the one
  intended for single square markers and reduces pose flips at distance.

### 21. Build writes tracked `.exe` files into the source tree (confirmed)

- **Where:** `src/saurcon_perception/CMakeLists.txt` (two `POST_BUILD` copy commands);
  `aruco_test.exe` and `aruco_class_test.exe` are committed.
- **Effect:** every build leaves the repository dirty.
- **Fix:** drop the copy commands and untrack the binaries; run the tests with
  `ros2 run saurcon_perception aruco_class_test`.
- **Also:** `aruco_class_test` uses paths relative to the current directory, so it only works
  when run from `src/saurcon_perception`.

### 22. ROS 1 leftovers in `middle_earth`

- **Where:** `src/middle_earth/scripts/teleop_vehicle.py` (`rospy`),
  `src/middle_earth/launch/basement_sim.launch` (roslaunch XML, `gazebo_ros`),
  `src/middle_earth/README.md` (ROS Noetic instructions).
- **Effect:** none of these run on ROS 2 Jazzy.
- **Fix:** port the teleop script to `rclpy` (useful when no gamepad is connected) or delete
  them.

### 23. Vehicle geometry mismatch in the Ackermann plugin

- **Where:** `src/middle_earth/models/rc_ackermann_vehicle/model.sdf`.
- **What:** the plugin has `wheel_separation` and `kingpin_width` of 0.14 m, but the wheels
  sit at y = ±0.08255 m (0.165 m apart). `config/vehicle_params.yaml` repeats 0.14 and is not
  read by anything.

### 24. Launch-file rough edges

- **Where:** `src/saurcon_rc/launch/`.
- **What:**
  - `find_workspace_root()` in `full_sim_saurcon.launch.py` only works when the package is
    built inside this workspace layout; `middle_earth` is not an installed package.
  - `saurcon.launch.py` and `sim_saurcon.launch.py` compute `bag_name` but never use it, so
    bags land in whatever directory the launch was started from.
  - `bringup.launch.py` runs `ctrl_interface`, which publishes `/ctrl_output` straight from
    the joystick with no state gating; running it alongside `saurcon_main` gives two
    publishers on that topic.
  - `/dev/ttyUSB0` and the baud rate are hardcoded.
  - `static_transform_publisher` uses the deprecated positional arguments.

### 25. Build artefacts and stale docs are tracked

- **What:**
  - `src/middle_earth/build/`, `install/` and `log/` (19 files) are committed.
  - `.vscode/` is in `.gitignore` but tracked, and points at `/home/wilson/saurcon_ws`.
  - `src/src/micro_ros_msgs` sits under a doubled `src/src/` path.
  - `src/saurcon_perception/README.md` describes an `include/` directory and an
    `aruco_detector_node` executable that do not exist.
  - `src/saurcon_rc/src/publisher_control_rc.cpp` (`talker`) is leftover tutorial code.

---

## Found during verification

### 26. Markers rendered too dark and with the wrong size; detector locked onto the plate edge

- **Where:** `src/middle_earth/worlds/racetrack.world` (marker materials),
  `src/saurcon_perception/config/marker_params.json`,
  `src/saurcon_perception/src/aruco_detector.cpp`.
- **What:**
  - The marker textures were lit only by scene lighting, so white cells rendered mid-grey
    and the standard detector could not decode them. Detection only worked through
    `detectInvertedMarker` plus a loose `errorCorrectionRate`.
  - The texture has a 10% white margin, so the black marker square is 0.122 m, not the
    0.1524 m plate. At close range the detector latched onto the plate edge (which matched
    0.1524 m); further away it latched onto the marker square (which did not).
  - OpenCV's `minMarkerDistanceRate` default discarded the real marker square at close
    range because it is only a few pixels inside the plate edge.
- **Effect:** correct range at 0.9 m, 12–21% too far at 1.4 m, no detection at 2.4 m.
- **Fix applied:** markers are self-lit (`emissive_map`), `marker_length` is 0.12192,
  inverted detection is off, `minMarkerDistanceRate` is 0.02. Measured range error is now
  about 1 cm at 0.9 m, 5 cm at 1.4 m and 15 cm at 2.4 m.

### 27. Ambiguous and distant marker poses fed to the filter with fixed 0.1 m noise

- **Where:** `aruco_detector.cpp` (`getTagsInImage`), `aruco_localizer_node.cpp`
  (`detectionCb`), `state_estimator.hpp` (process noise).
- **What:** a small marker can be explained by two orientations mirrored about the line of
  sight. Picking the wrong one puts the vehicle up to a metre to one side. Every fix was
  published with the same 0.1 m / 0.1 rad noise regardless of distance.
- **Effect:** the original filter hid this because it gave position no process noise and so
  ignored fixes after start-up. Once the filter was allowed to use fixes (issue 3), the
  estimate jumped by up to 1.6 m.
- **Fix applied:** the detector drops detections whose two candidate poses differ by more
  than 15° and cannot be told apart; the localizer scales noise by
  `1 + (range / 1.5 m)^2`; markers under ~13 px are ignored; the innovation gate is
  5 sigma and position process noise is `0.01 + 0.05·|v|` m/√s.
