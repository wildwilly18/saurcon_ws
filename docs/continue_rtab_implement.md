# Continue RTAB-Map implementation

> Historical handoff. Implementation resumed on 2026-11-12. See
> [RTABMAP_STATUS.md](RTABMAP_STATUS.md) and [RTABMAP_USAGE.md](RTABMAP_USAGE.md)
> for current results and commands; the state below describes the earlier pause.

Handoff written 2026-11-12. The user requested pausing implementation to continue
in another Codex session, potentially from their phone.

## Objective and source of truth

Read [RTABMAP_PLAN.md](RTABMAP_PLAN.md) first. Implement its simulation work:
an OAK-D Lite model/interface, wheel/gyro odometry, RTAB-Map mapping and
localization, and measured comparison against the existing ArUco baseline.
Real hardware deployment (Phase 6) is deferred. Retire ArUco only after the
performance gate in the plan passes; do not delete it prematurely.

Workspace: `/home/wilson/Code/saurcon_ws`.
Branch: `main`, HEAD: `e6004cf356f250ad1144fdb663bd0af23e8a7b08`.
No commits were made during this session.

## Actual changes made

Only these three tracked files were edited:

- `src/saurcon_nav/src/state_estimator.hpp`: constructor accepts
  `bool use_aruco = true`; stores the selection.
- `src/saurcon_nav/src/state_estimator.cpp`: when ArUco is disabled, SURVEY
  initializes at `(0,0,0)` with small initial pose uncertainty and immediately
  enters NAVIGATE. Sensor initialization and stationary gyro bias calibration
  still happen first. ArUco measurements are ignored in this mode. The existing
  UKF prediction and process-noise propagation remain in use.
- `src/saurcon_nav/src/state_estimator_node.cpp`: declares ROS parameter
  `use_aruco` (default true), passes it into the estimator, and subscribes to
  ArUco only when enabled. With `use_aruco:=false`, publishes odometry and TF in
  `odom` with child `base_link`, and adds `/saurcon/odom_nav`. The existing
  `/saurcon/nav_state` output remains available and uses the selected frame.
  Copies all planar pose covariance terms, including cross terms, into the
  ROS covariance. Sets unestimated pose/twist axes to large variances.

These edits are **not built or tested**. Review the diff before continuing.
No launch currently selects the new mode, so existing launches retain ArUco
behavior by default. The covariance changes apply to both modes.
Yaw-rate twist is still not populated; review whether consumers need it.

`docs/` and `scripts/sim_eval/` were already untracked before work began.
They contain the user's plan and baseline harness; preserve them. Apart from
this handoff, no documentation or harness changes were made in this session.
Despite an earlier progress update describing harness cleanup as underway,
that cleanup was not implemented.

## Environment and installation status

- Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic; existing `build/` and `install/`
  directories are present. Their binaries do not include these new edits.
- RTAB-Map is **not installed**, confirmed with `dpkg-query` at handoff time.
- An attempted `sudo -n apt-get install -y ros-jazzy-rtabmap-ros` failed because
  sudo needs a password. Nothing was installed by that attempt.
- A subsequent attempt to create `/tmp/saurcon-askpass.sh` and install through
  `zenity --password` was interrupted. The helper does not exist at handoff.
  `zenity` is available. Do not assume the installation ran.
- Initial tool calls failed because the sandbox could not initialize
  (`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`). The user
  subsequently disabled sandboxing; current shell commands work normally.
  Use the next session's actual permissions, not the earlier escalation flags.
- No simulation was launched, no baseline was reproduced, no tests were run.
- No AGENTS.md was found by the repository/parent search in this session.

## Findings from inspection

- Estimator implementation is C++, not Python. It already initializes sensor
  inputs, estimates gyro bias, and runs a four-state UKF `[X,Y,Theta,V]` using
  wheel speed and gyro as process inputs. Its old no-ArUco timeout initializes
  with huge global-pose uncertainty; the explicit new odometry mode avoids that.
- `src/saurcon_rc/launch/full_sim_saurcon.launch.py` currently launches the
  Gazebo GUI, bridge, joystick/controller, sim RC, both ArUco nodes, estimator,
  static `base_link -> camera_link` / `imu_link` transforms, and bag recording.
  It locates the workspace through `SAURCON_WS` or upward directory search.
- The vehicle's generic RGB-D camera is at the end of
  `src/middle_earth/models/rc_ackermann_vehicle/model.sdf`: 640x400, 15 Hz,
  horizontal FOV 1.204 rad, clip 0.1–10 m, image Gaussian noise stddev 0.007,
  mounted relative to `rear_axle_center` at `(0.219,0,0.05)`.
- Current bridge config publishes `/camera/image`, `/camera/depth_image`,
  `/camera/camera_info`; no OAK model or OAK bridge entries exist yet.
- ArUco calibration comes from
  `src/saurcon_perception/config/camera_params.json`, with fx/fy 465.74,
  principal point (320,200), and the above mounting transform. Keep this
  consistent with any changed camera when rerunning the ArUco comparison.
- `scripts/sim_eval/runsim.sh` has unsafe broad process-name cleanup, weak
  path quoting, and deletes prior output. Replace cleanup with tracked process
  groups and traps; use a fresh output directory for each measurement.
- `analyze.py` assumes two directories `run_orig`/`run_fixed`, a 47-second lap,
  and nonempty ArUco/frame arrays. Make it accept run paths and pose sources,
  and handle absent ArUco data. Its ground-truth speed timestamps also appear
  to subtract the time origin twice; review this while fixing evaluation.
- Logger currently uses wall-clock receipt times. Record message/simulation
  timestamps and sample TF at matching times for meaningful SLAM scoring.
  Ground truth converts model origin to rear axle by subtracting 0.127 m
  along the heading. It and the driver assume the first ground-truth transform
  is the car; prefer matching the model name explicitly.
- Driver currently supports one lap only and includes controller-loss tests.
  Add explicit lap-count/direction controls for mapping and evaluation.

## Research status

Research was started, but the hardware/driver contract is **not verified** and
no interface table has been written yet. Several Luxonis documentation and
raw GitHub URLs failed to load. Do not treat remembered specifications in the
original plan as verified results.

Useful primary sources found:

- https://github.com/luxonis/depthai-ros
- https://docs.luxonis.com/software-v3/depthai/ros/driver
- https://docs.luxonis.com/software-v3/depthai/ros/parameters
- https://checkout.luxonis.com/products/oak-d-lite-1
- https://raw.githubusercontent.com/introlab/rtabmap/master/corelib/include/rtabmap/core/Parameters.h

The last source was readable, but is upstream master, not validation against
the installed Jazzy release. Check the actual driver's branch/version and
configured pipeline: stream names, resolution, alignment, and rates are
configuration dependent. Preserve the user's confirmation that their device
has an IMU. Verify dimensions, mass, lens positions, baseline and frame names
before implementing the model.

## Next steps, in order

1. Review the working-tree diff and build `saurcon_nav`. Add focused checks for
   startup without ArUco, origin initialization, straight/turning integration,
   growing finite covariance, ignored ArUco fixes, and unchanged default mode.
   Check actual odometry/TF frame ownership. Example build:
   ```bash
   source /opt/ros/jazzy/setup.bash
   colcon build --symlink-install --packages-select saurcon_nav
   source install/setup.bash
   ```
2. Make the lap harness portable and safe, parameterize outputs, and reproduce
   the existing camera/ArUco baseline before replacing the sensor. The plan's
   reference figures (0.05 m RMS, 0.19 m max, 1.4 degrees RMS) are historical,
   not measured in this session. Preserve run logs and analysis artifacts.
3. Finish the verified OAK-D Lite interface table in the original plan. Choose
   a documented real-driver configuration suitable for simulation, including
   aligned image/depth dimensions, encodings, timestamps and camera TF tree.
4. Implement the reusable OAK model, attach it with a fixed joint, bridge all
   streams, and publish matching static TF. Add depth postprocessing with
   range-squared noise, invalid depth and a documented low-texture model;
   convert float metres to the driver's depth encoding. Preserve legacy
   camera topics while ArUco comparison is needed. Document approximations
   and unmodelled effects in the model folder.
5. Verify camera intrinsics/baseline, frame IDs, synchronization, depth
   alignment and wall distances, IMU gravity/yaw signs, then rerun ArUco and
   dead-reckoning laps. Support headless simulation in the launch/harness.
6. Install RTAB-Map when sudo authentication is available, and declare its
   dependencies in setup/package files. Add a mapping/localization launch
   with wheel/gyro odometry, OAK RGB/depth topics, `map -> odom` ownership,
   2-D occupancy output and configurable database path. Verify parameters
   against the installed version. Keep database deletion explicit and
   confined to fresh mapping runs; localization must preserve the database.
7. Record TF `map -> base_link`, score against ground truth with a single
   start-pose SE(2) alignment, and run two mapping laps. Check accepted loop
   closures and occupancy geometry, then evaluate saved-map localization,
   alternate starts, reverse travel and a marker-free world.
8. If needed, tune features/depth/loop-closure thresholds or compare visual
   odometry as the plan describes. Only after RTAB-Map meets the baseline,
   retire ArUco and update README/BUGS and plan status. Leave hardware work
   deferred. Record unresolved validation honestly if environment limits
   prevent completing it.

## Moving to another session

Suggested prompt: “Read `docs/continue_rtab_implement.md` and
`docs/RTABMAP_PLAN.md`, inspect the existing changes, and continue the
implementation and validation.”

This handoff and all implementation edits are local and uncommitted. A session
using a different checkout will need the files/diff transferred or committed
and made available there. No push or remote synchronization has been done.
