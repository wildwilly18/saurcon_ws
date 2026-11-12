# RTAB-Map implementation status — 2026-11-12

The section below headed "Update 2026-11-12 (afternoon)" supersedes the
results further down where they differ.

Implementation is available; the accuracy gate for removing ArUco is not yet
passed. Real-vehicle deployment remains deferred. Usage is documented in
[RTABMAP_USAGE.md](RTABMAP_USAGE.md).

## Update 2026-11-12 (afternoon) — continued by Claude

Codex's last run (map two laps forward then two in reverse, to fix the reverse
failure) had finished but was never scored. Scored, it was 0.50 m RMS / 1.28 m
max. Three causes were found and fixed:

1. **Gyro bias calibrated from only 1 s of samples.** The simulated gyro has no
   bias, only 0.009 rad/s noise, so a 100-sample average leaves a random bias
   error near 0.001 rad/s, which drifted heading ~13° over the 216 s run. Earlier
   runs that looked good were partly luck of that draw. `saurcon_nav` now keeps
   refining the bias with every IMU sample taken while the wheels are stopped
   (an Ackermann car cannot yaw when stationary), gated at 0.1 rad/s against
   knocks. Unit-tested (`test_dead_reckoning.cpp`).
2. **Accumulated odometry covariance passed to RTAB-Map as per-link covariance.**
   The filter's total covariance grows to metres; RTAB-Map reads odometry
   covariance as the uncertainty of each link between nodes, so a false loop
   closure between the look-alike y=0 and y=4 aisles (a 4 m jump) passed
   `RGBD/OptimizeMaxError`. RTAB-Map now reads odometry from TF with fixed
   `odom_tf_linear_variance` 2.5e-5 and `odom_tf_angular_variance` 1e-5
   (5 mm, 0.18° per link). 2 cm per link was still loose enough to accept the
   false closure. These values are sim-derived; re-measure on hardware.
3. **No way to give a start pose in localization mode.** Added launch argument
   `initial_pose:="x y z roll pitch yaw"` (map frame, localization only,
   guard-tested in `test_launch_guards.py`).

### Results with these fixes (single runs, same scripted path)

| Run | Position RMS | Max | Heading RMS | Notes |
|---|---:|---:|---:|---|
| Mapping, 2 laps forward + 2 reverse (216 s) | 0.113 m | 0.383 m | 0.50° | 46 closures accepted, 114 rejected; end error 4 mm. Odometry alone 0.183 m RMS |
| Localization forward, saved two-direction map | 0.037 m | 0.065 m | 0.14° | |
| Localization reverse, known start (`initial_pose`) | 0.101 m | 0.188 m | 0.60° | |
| Localization reverse, unknown start | 3.49 m | 14.6 m | 85° | Wrong relocalization while parked; correct (≤0.1 m) from 10.7 s after moving off |
| Mapping, marker-free world, 2 laps (96 s) | 0.059 m | 0.077 m | 0.14° | 35 closures accepted (previously none). Odometry alone 0.065 m RMS |

Runs are in `evaluation/bidir_v4/`, `evaluation/markerfree_v2/`; maps in
`maps/bidir_v4*.db`, `maps/markerfree_v2.db` (all git-ignored). Reverse runs use
`evaluation/worlds/reverse.world` from `make_world.py --yaw 3.14159`.

### UKF fused with RTAB-Map (added later the same day)

The UKF now uses RTAB-Map to localize: a second, map-frame UKF fuses RTAB-Map's
pose and owns `map -> odom` (see RTABMAP_USAGE.md, frame ownership). Marker-free
world, two laps, 101 s of driving (`evaluation/ukf_fused_markerfree_v2/`):

| Estimate | Position RMS | Max | Heading RMS |
|---|---:|---:|---:|
| UKF fused with RTAB-Map (`/saurcon/nav_state`, 50 Hz) | 0.070 m | 0.145 m | 0.28° |
| RTAB-Map pose (filter input, ~2 Hz) | 0.069 m | 0.156 m | 0.30° |
| Odometry-only UKF | 0.168 m | 0.438 m | 1.19° |

Position errors stay inside the fused filter's ±3σ; heading is somewhat
over-confident (74% of samples inside ±3σ). The fused filter has no gyro-bias
state, so it cannot learn bias from RTAB-Map's heading. Not yet tested with
fusion: localization mode (uses `/rtabmap/localization_pose`), reverse and
two-direction runs. Plots: `scripts/sim_eval/plot_ukf.py <run> <out>`.

### What is still open

- **Global relocalization from an unknown pose** in this symmetric warehouse.
  While stationary, RTAB-Map's odometry-cache check cannot reject a look-alike
  match, so it accepted the view facing −x as the place 5 m away facing +x.
  Options: require motion before accepting the first localization, raise
  `Vis/MinInliers` for localization, or rely on a known start pose (last saved
  pose / operator-set pose), which is what a real deployment would normally do.
- **Reverse RMS (0.10 m) is about twice the ArUco baseline RMS (0.05 m)**,
  although the maximum (0.19 m) matches it. Whether that clears the gate for
  removing ArUco is Wilson's call.
- Odometry in sim is near-perfect wheel speed plus noise-only gyro; real wheel
  slip and gyro bias drift will be larger.

## Implemented

- Wheel/gyro UKF mode (`use_aruco:=false`) initializes at the odometry origin,
  ignores ArUco, publishes `odom -> base_link` and `/saurcon/odom_nav`, including
  planar cross covariances and bias-corrected yaw rate. Default ArUco mode stays
  available. Plane constraints have finite covariance; marking roll/pitch as
  unbounded caused RTAB-Map to discard useful angular information.
- Reusable OAK-D Lite SDF, RGB and grayscale stereo pair, 75 mm baseline,
  RGB-aligned depth, IMU, optical TF, CameraInfo and legacy topic aliases.
  Depth is 16UC1 millimetres with invalid zeros, range-squared disparity noise
  and a low-texture invalidity proxy. Hardware/model differences are explicit
  in the model README; this is not a calibrated hardware twin.
- RTAB-Map 0.23.13 installed and dependencies declared. Mapping/localization
  launches, database guards, occupancy grid, headless launch and frame-owner
  validation. g2o is selected; neighboring visual refinement is disabled to
  retain the measured wheel/gyro constraints. Minimum inliers is 20.
- Portable lap runner, scoped cleanup with escalation for its own stubborn
  children, run lock, unique Gazebo partitions and separate ROS domain. Custom
  Gazebo ground-truth bridge preserves vehicle name and capture timestamp.
- Multi-lap/reverse driver, generated alternate-start and marker-free worlds,
  timestamped TF scoring, fixed mapping-origin alignment for localization,
  JSON metrics, plots, optional annotated video, occupancy and closure capture.

## Verified

- Both changed ROS packages build. All three CTest suites pass: dead reckoning,
  depth behavior and localization database guards. SE(2) scoring was checked
  against a synthetic rotated/translated trajectory.
- Actual Gazebo OAK model wall-depth fixtures: 0.5 m → 0.499515 m,
  1 m → 0.999251 m, 2 m → 2.000084 m, 4 m → 4.000103 m.
- Live RGB/mono/depth encodings and frame IDs, CameraInfo focal lengths,
  principal points, right-camera baseline, aligned capture stamps and optical
  transform checked. IMU stationary gravity points +Z. Capture intervals match
  configured rates within simulation-step quantization. Best-effort image
  delivery can drop under SLAM load; sensor JSON reports actual median rates.
- Original generic-camera baseline reproduced before replacement: 0.04946 m
  RMS position, 0.17205 m max, 0.9806 degrees RMS heading (old receipt-time logger).
- Clean OAK/ArUco run: 0.08729 m RMS position, 0.13945 m max, 0.1829 degrees
  RMS heading over 47 seconds, using timestamp-preserving ground truth.
- Clean two-lap mapping: 55 accepted closures, 0.08635 m RMS position,
  0.18610 m max, 0.2605 degrees RMS heading over 94 seconds. Odometry alone
  on that run: 0.10602 m RMS, 0.18206 m max. End error: mapping 0.03920 m;
  odometry 0.11062 m. Grid: 609×217 cells at 0.05 m, 9,680 occupied cells.
  The rendered grid shows the rack rows and aisle layout; no claim of a
  surveyed occupancy-cell accuracy measurement is made.

## Completed scenario results

All results use the same scripted path. Localization uses one fixed map-to-world
transform obtained from the mapping run, not an alignment fitted to each new lap.
These are single-run measurements, not statistical performance guarantees.

| Scenario | Position RMS | Maximum | Heading RMS | Result |
|---|---:|---:|---:|---|
| Forward saved-map localization | 0.04389 m | 0.06210 m | 0.1786° | Meets original target |
| Alternate start, x=3.5 m, forward | 0.04450 m | 0.07933 m | 0.2045° | Meets original target |
| Reverse against forward-only map | 16.0819 m | 26.1712 m | 179.2258° | Failed global localization |
| Marker-free mapping, one lap | 0.40756 m | 0.80063 m | 2.7381° | No accepted global closure; odometry drift |

Visual-odometry fallback on the marker-free lap lost tracking. Only 83 map-pose samples were available, with a 34.85-second gap.
Intervals no longer than 0.25 seconds totalled 7.39 seconds of observation
within the 47-second scoring window. RMS error on available samples was 4.01 m. This is a failure,
not a full-lap accuracy result. Wheel/gyro odometry remains the default.
The reverse and marker-free failures block ArUco retirement. Three accepted
visual matches during reverse travel did not establish a correct pose; pose
error, rather than match counts alone, is the acceptance measure.

Saved databases are under `maps/` (including `clean.db` and
`clean-markerfree.db`). Reports, plots, occupancy image, annotated forward
localization video and copied run logs are under `evaluation/`. These generated
artifacts are intentionally ignored by Git. Original runs are in
`/tmp/saurcon-clean-*`. RTAB-Map can save last-localization metadata even in
localization mode; copy a map database before independent experiments if its
startup state must remain identical.

## Discarded development measurements

Earlier `/tmp/saurcon-mapping-*` and `/tmp/saurcon-oak-*-final` development runs
must not be used as acceptance evidence. A failed launch left another Gazebo
instance alive, the standard Pose_V bridge lost timestamps, and early covariance
settings produced underconstrained GTSAM optimization. The harness now isolates
runs, preserves timestamps, closes lock descriptors in children and forcibly
cleans up only its own process groups. The discarded results are retained for
debugging, not presented as clean accuracy measurements.

## Remaining acceptance work

- Standard and alternate-start localization meet the original target, but
  reverse and marker-free robustness must improve before retiring ArUco.
- Any required feature/loop-closure tuning should use fresh named databases and
  preserve the baseline. A reverse-view map may require mapping in both travel
  directions. Marker-free passive stereo is deliberately less informative.
- Simulated IMU yaw sign matched the car IMU on all 583 sampled turning
  messages (correlation 0.9884). Calibrated real-device extrinsics/rates remain
  to be checked on hardware; the existing car IMU drives navigation here.
- Phase 6 hardware deployment and conditional Phase 7 deletion are not claimed
  complete. No commits or pushes have been made.

## Phase summary

| Plan phase | Outcome |
|---|---|
| 0: measuring stick | Portable runner; original baseline reproduced; timing/isolation corrected |
| 1A/B: OAK and sensor readiness | Model, ROS interface, noise, TF and wall checks implemented; calibration approximations documented |
| 2: wheel/gyro odometry | Implemented and regression tested |
| 3: mapping | Two laps, accepted closures, saved database and occupancy grid verified |
| 4: localization/evaluation | Standard and alternate starts pass; reverse and marker-free limitations measured |
| 5: fallbacks | Optimizer/refinement tuning and visual-odometry comparison performed; visual fallback loses tracking |
| 6: hardware | Deferred as requested |
| 7: remove ArUco | Deferred because robustness tests fail; existing path preserved |
