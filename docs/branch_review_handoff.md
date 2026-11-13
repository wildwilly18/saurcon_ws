# Branch review: fix-agent handoff

> **Later change (2026-11-13):** the ROS 2 RL nodes were removed. `policy_node.py` is gone;
> `cone_policy_node.py` became `src/saurcon_plan/saurcon_plan/cone_follower_node.py`
> (classical follower only); `cone_follower.py`, `cones.py`, `track.py` and
> `cone_mapper_node.py` moved to `src/saurcon_plan/saurcon_plan/`; the watchdog tests are in
> `src/saurcon_plan/test/test_follower_node.py`. Paths below are as they were at review time.

Reviewed 2026-11-13. This document records findings and proposed acceptance checks; **none of the fixes has been implemented**.

## Scope and workspace

- Repository: `/home/wilson/Code/saurcon_ws`
- Branch: `rl-racing-mujoco-cones`
- Reviewed HEAD: `cefc36c`
- Comparison base: `main` at `e6004cf`
- Scope includes the branch commits **and the existing uncommitted/untracked implementation**. Line numbers below refer to that working-tree snapshot; locate the named methods if they move.
- Preserve existing work. Do not reset or discard the dirty tree. In particular, `cone_follower.py` and `gazebo_cone_env.py` are untracked implementation files, not disposable review artifacts.

The review found two P1 control-safety issues and four P2 correctness issues. Fix the two watchdog failures first. The existing `/auto_cmd` timeout protects against a silent publisher; it does not protect against a live policy repeatedly publishing commands based on stale inputs.

## 1. P1: map policy drives indefinitely after navigation updates stop

**Location:** `src/saurcon_rl/saurcon_rl/policy_node.py`, `on_state()` and `step()`, approximately lines 52–83.

`on_state()` stores pose and velocity without their timestamp or receipt time. `step()` only tests `self.state is None`. Once one state has arrived, the 20 Hz timer keeps calling the policy and publishing `/auto_cmd`, even if the estimator has died. Those commands continually refresh the RC state machine's 0.25 s command watchdog.

**Reproduced:** a fake policy returning action `[0, 0]`, with one stored navigation state and no further navigation callbacks, produced 200 successive commands at 6 m/s. These were direct method calls with a fake publisher; no vehicle was actuated.

**Suggested fix:** track navigation freshness, reject stale/invalid state updates, and publish a zero command whenever a required state is missing or expired. Make the timeout explicit/configurable. Reset command-history/steering-estimate state as needed so recovery does not reuse an obsolete command. Keep the downstream RC watchdog.

**Acceptance checks:**

- Before the first valid state, the node cannot command motion.
- Fresh state permits normal policy output.
- Advancing the clock beyond the timeout without another state produces zero linear and angular commands on every subsequent step.
- Repeated delivery of old-stamped messages does not indefinitely renew validity.
- Fresh valid data permits deliberate, tested recovery.
- Exercise the behavior without physical actuation, using a fake clock/policy/publisher or an isolated ROS test domain.

## 2. P1: cone policy drives with stale or missing odometry/TF

**Location:** `src/saurcon_rl/saurcon_rl/cone_policy_node.py`, `on_odom()`, `process_pending()`, `detect()`, and `step()`; especially lines 190–199.

Only camera processing freshness gates motion. Odometry velocity has no freshness check. `process_pending()` falls back to the latest available odometry transform after `tf_wait`, regardless of that transform's age. `step()` clamps transform age to 0.2 s rather than rejecting it, and substitutes an identity transform when lookup fails. `detect()` marks images fresh at processing time, which can also hide old image capture times.

Consequently, cameras can continue refreshing the control loop after odometry stops, while cone positions are transformed with an obsolete pose. This affects both learned and classical cone controllers.

**Reproduced:** with current time 100 s, a fresh processed-image timestamp, and an odometry TF stamped at 1 s, `step()` published 6 m/s. Its reported lag was only 200 ms because of the clamp.

**Suggested fix:** require fresh odometry messages, a valid sufficiently recent control transform, and a sufficiently recent image capture timestamp. Bounded latency extrapolation may remain for normal lag, but do not turn arbitrarily old transforms into apparently valid ones by clamping their age. Missing transforms must lead to a stop, not an identity-pose substitution. Review the pending-image fallback so it cannot bypass these checks; reset or invalidate cone memory when its coordinate basis becomes unreliable.

**Acceptance checks:**

- Fresh images plus expired odometry produce a stop.
- Fresh odometry messages plus expired TF produce a stop.
- A failed TF lookup produces a stop.
- Delayed image processing does not renew an already expired camera capture.
- Normal bounded sensor/TF latency still permits driving.
- Test both classical and learned policy paths, including recovery after a data interruption.

## 3. P2: global map-to-odom TF combines different timestamps

**Location:** `src/saurcon_nav/src/state_estimator_node.cpp`, `spin_cb()`, approximately lines 250–262.

The global filter predicts and stamps its pose at `now`, but constructs `map -> odom` using `lookupTransform("odom", "base_link", tf2::TimePointZero)`. The latest odometry pose can be older than `now`. Combining those poses embeds the vehicle's intervening motion in the map correction. Once odometry for the current timestamp arrives, composing the TF chain disagrees with the published global navigation state.

**Reproduced using a TF buffer:** global x = 10 m at t = 2 s; latest odometry x = 9.5 m at t = 1.9 s. The current formula publishes map-to-odom x = 0.5 m at t = 2 s. When odometry x = 10 m at t = 2 s arrives, map-to-base becomes 10.5 m instead of 10 m. This represents 100 ms lag at 5 m/s, even with otherwise perfect estimates.

**Suggested fix:** compute the correction from global and odometry poses evaluated at the same timestamp. Possible designs include queuing the global pose until matching odometry is available, or maintaining enough state history to evaluate both at a common time. Merely changing the outgoing timestamp while still mixing poses from different times does not fix the geometry. Do not block a callback waiting for data that needs that callback's executor to progress.

**Acceptance checks:**

- With identical global/odom trajectories, the correction remains identity despite delayed odometry delivery.
- At a shared timestamp, `map -> odom -> base_link` matches the global navigation pose within numerical tolerance.
- Cover translation and turning, varied message arrival order, and unavailable historical TF.
- Preserve one publisher per TF edge and keep RTAB-Map corrections out of its odometry input.

## 4. P2: map-policy origin is wrong under default ArUco localization

**Locations:** `src/saurcon_rl/saurcon_rl/policy_node.py`, `on_state()`, approximately lines 56–60; `src/saurcon_rc/launch/full_sim_saurcon.launch.py`, `policy()`, approximately lines 92–105.

The policy always applies its default map origin `[-1.127, 0, 0]`. This is appropriate for an RTAB map built from the usual spawn, but ArUco localization already returns coordinates based on the world marker map. The full simulation launch accepts `policy_model:=...` while retaining its default `use_aruco:=true`, and neither adjusts the origin nor rejects that combination.

**Reproduced:** feeding the policy an ArUco/world pose at x = -1.127 m produces a policy world position of -2.254 m. This shifts the track-relative observation and turn locations by 1.127 m. Both sources can use the frame name `map`, so checking only `header.frame_id` cannot distinguish their origin conventions.

Also review `fuse_slam:=false` and visual-odometry configurations: their `/saurcon/nav_state` is odometry, not the corrected map pose expected by this policy.

**Suggested fix:** explicitly configure the policy pose source and origin for supported launch modes, or reject incompatible combinations before starting the policy. Expose the map-origin configuration through the launch if RTAB maps may start at different poses. Avoid silently interpreting odometry as a global map pose.

**Acceptance checks:**

- ArUco/world coordinates are not shifted twice, or that mode is explicitly rejected for this policy.
- Standard RTAB localization still converts map origin `(0, 0)` to world `(-1.127, 0)`.
- A non-default map origin is configurable and tested if supported.
- Unsupported estimator/policy combinations fail early with an actionable error.

## 5. P2: zero-distance path interpolation corrupts cone curvature

**Location:** untracked `src/saurcon_rl/saurcon_rl/cone_follower.py`, `along()`, approximately lines 143–155, and its caller `max_curvature()`.

At `dist == 0`, `np.searchsorted(s, dist) - 1` yields -1. Interpolation then uses the last path segment and wraps to the first point. The first curvature sample requests distance zero on every call, so this is an exercised boundary, not merely an unused helper edge case.

**Minimal reproduction:**

```python
import numpy as np
from saurcon_rl.cone_follower import ConeFollower
path = np.array([[0., 0.], [1., 0.], [1., 1.]])
print(ConeFollower.along(path, 0.0))  # actual [3., 3.]; expected [0., 0.]
```

For a 0.9 m path with a 1 rad bend after its first 0.3 m, the current maximum-curvature estimate was approximately 0.346 /m; correcting just the zero-distance result gave approximately 1.958 /m. Incorrect curvature feeds the speed-planning calculation. The exact effect on commanded speed also depends on its other limits.

**Suggested fix:** handle the starting boundary explicitly or use bounded segment selection. Define behavior for negative distance and degenerate segments consistently with the helper's intended contract.

**Acceptance checks:** zero distance returns the first point; interior interpolation, exact vertices, the endpoint, and beyond-end extrapolation remain correct. Add a short bent-path curvature regression, not just a helper-only assertion.

## 6. P2: non-SLAM race videos crash on an empty map history

**Location:** uncommitted changes to `scripts/sim_eval/make_race_video.py`, map-panel activation around lines 118–125 and `MapPanel.render()`; related producer: `scripts/sim_eval/capture_map.py`.

`runsim.sh` starts map capture for every run. The capture script now creates `maps/index.csv` even when SLAM is disabled and no map arrives. The video script treats existence of that file as evidence that a map panel can be rendered. With no `map` rows in `log.csv`, `self.path` is a one-dimensional empty array and `self.path[:, 0]` raises an exception.

**Reproduced:** a temporary run containing a header-only map index and a ground-truth-only log raised `IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed` when rendering the panel.

**Suggested fix:** activate the panel based on actual map records, and make its internal arrays/rendering tolerate missing trajectory and cone data. A valid map can exist before any trajectory samples, so both the activation check and empty-array handling matter.

**Acceptance checks:**

- A normal non-SLAM run produces the onboard/chase video without a map panel.
- A header-only map index is handled without crashing.
- A valid grid with no map trajectory renders safely.
- A SLAM run with grid, trajectory, and cone records still renders the intended panel.

## Validation already performed

- Rebuilt `saurcon_nav` and `saurcon_rc` successfully.
- All three navigation CTest targets passed: `dead_reckoning`, `launch_guards`, and `depth_model`.
- `RaceEnv`, `MujocoRaceEnv`, and `MujocoConeEnv` passed Gymnasium `check_env(..., skip_render_check=True)` and short finite-observation/reward smoke runs on all four tracks. Gymnasium warned about unbounded observation spaces; the checks did not fail.
- The targeted reproductions described above ran without vehicle actuation. They were temporary snippets, not committed regression tests.
- Full Gazebo localization/racing runs were **not** repeated as part of this review. Existing passing tests do not cover the watchdog failures or global TF timestamp consistency.
- `git diff --check main` reported whitespace issues, largely CRLF CSV data plus whitespace in `sysid.world`; these were not treated as functional findings.

Useful commands from the repository root:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
colcon build --packages-select saurcon_nav saurcon_rc --cmake-args -DBUILD_TESTING=ON
colcon test --packages-select saurcon_nav saurcon_rc --event-handlers console_direct+
colcon test-result --verbose

# Use the current source tree with the RL environment for targeted Python checks:
PYTHONPATH="$PWD/src/saurcon_rl:$PYTHONPATH" .venv-rl/bin/python path/to/test_script.py
```

## Cross-check by the implementing session (2026-11-13)

The author of the in-progress work re-checked each finding against the same working tree. The review was written at 05:15, after the last source edit at 04:41, so its snapshot is current. No fixes were made.

| # | Status | Notes |
|---|--------|-------|
| 1 | Confirmed | `policy_node.py` `step()` only checks `self.state is None`; `on_state()` keeps no stamp. |
| 2 | Confirmed | `cone_policy_node.py` `step()`: lag clamped by `min(..., 0.2)`, identity pose on `TransformException`, `on_odom()` unstamped. `detect()` also writes cone memory and `last_image` with processing time, not `rgb_msg.header.stamp`. |
| 3 | Confirmed | `state_estimator_node.cpp` `spin_cb()` composes the global pose at `now` with `lookupTransform(..., TimePointZero)`. |
| 4 | Confirmed | `map_origin` defaults to `[-1.127, 0, 0]`; `policy()` in `full_sim_saurcon.launch.py` neither sets it nor rejects `use_aruco:=true`. |
| 5 | Confirmed; worse on short paths | `along(path, 0.0)` returns `[3, 3]` for the doc's example. For a 0.3 m straight followed by a 1 rad arc of radius 0.6 m (expected κ ≈ 1.67 /m), `max_curvature()` returned **0.013 /m**. The 0.4 m step leaves only one sample on a 0.9 m path, and that sample's first point is the wrapped value. The speed limit then comes from `v_stop`/`v_steer` instead of the curve. Short paths are typical in bends, which is where the classical follower ran wide under SLAM load. Fix this first: it may account for some of those failures. |
| 6 | Confirmed | `capture_map.py` writes the `index.csv` header unconditionally; `make_race_video.py` activates the panel on file existence. `self.path[:, 0]` fails when there are no `map` rows. |

### In-scope change the review did not cover

`src/saurcon_nav/launch/rtabmap_sim.launch.py` (uncommitted). These settings were added to fill the occupancy grid:

```python
'Grid/RayTracing': 'true',
'Grid/FootprintLength': '0.45', 'Grid/FootprintWidth': '0.30', 'Grid/FootprintHeight': '0.25',
'GridGlobal/FootprintRadius': '0.25',
```

Measured on the no-marker world, classical follower, 3 laps:

- **Unknown cells inside the track rectangle:** 49% before, 11–14% after.
- **Driving:** two clean runs after the change. Run directories: `evaluation/cones_gz/classical_slam_rt` and `classical_slam_rt2`; the baseline is `classical_slam`.
- **CPU cost:** the cone node's camera rate fell from 11.0 to 9.5–9.9 frames/s, and stale control steps rose from 3.3% to 4–5%. This feeds finding 2: under load the stale-input paths are exercised more often.

Points for the reviewer:

- **Footprint geometry.** The footprint box is centred on `base_link`, which is at the rear axle, so it covers about ±0.225 m around the axle rather than the car body. Points are only filtered inside it; the camera never sees the car, so the visible effect is nil. It is still geometrically wrong for the real car. Consider an offset, or use `GridGlobal/FootprintRadius` alone.
- **Scope.** Only the simulation launch is changed; there is no separate hardware RTAB-Map launch in `saurcon_nav/launch/`. `test_launch_guards.py` passes after the edit (3 passed).
- **Hardware.** Ray tracing with `Grid/RangeMax 4.0` on real OAK-D stereo will trace through noisy depth. Validate on hardware before enabling it there.
- **Chase video.** Race videos need `CHASE=1` for `runsim.sh`; otherwise `make_race_video.py` fails with `FileNotFoundError: .../chase/stamps.csv`. This is a usability gap rather than a bug, but the finding-6 fix could make the chase panel optional in the same way.

### Suggested fix order

1. Findings 1 and 2: safety.
2. Finding 5: a one-line boundary fix, likely to affect classical-follower bend behaviour. Re-run `cone_race.sh classical ... slam:=true` afterwards.
3. Findings 6, 4 and 3.

## Fixes (2026-11-13, implementing session)

All six findings are fixed, in the order 1, 2, 5, 6, 4, 3. Nothing is committed yet. For review:

| # | Fix | Regression tests |
|---|-----|------------------|
| 1 | `policy_node.py`: a state counts only if its header stamp is newer than the last accepted one, within `state_timeout` (0.25 s) of the clock, and finite. Without a fresh state, every step publishes a zero `Twist` and resets `prev_action`/`steer_est`. A clock going backwards clears the stamp. | `src/saurcon_rl/test/test_input_watchdogs.py` (`map_policy_*`): no motion before the first state; drives on fresh state; 200 zero commands after expiry; repeated or older stamps do not renew; NaN rejected; recovery; origin applied once. |
| 2 | `cone_policy_node.py`: new `inputs()` gate. It requires an image *captured* within `image_timeout`, an odometry message stamped within `odom_timeout` (0.25 s), and an `odom -> base_link` transform no older than `tf_timeout` (0.25 s). There is no clamp and no identity fallback. Cone memory and `last_image` use the image stamp. The pending-image fallback uses the latest pose only within `tf_fallback_max` (0.1 s) of the image, and otherwise drops the image. A missing or expired transform clears the cone memory; any stale input resets the command history and the follower's held command. | `test_input_watchdogs.py` (`cone_policy_*`, classical and learned): expired odometry, expired TF, failed lookup, the review's 100 s / 1 s case, late processing of an old image, fallback-pose distance, normal 100 ms lag still drives, recovery. |
| 5 | `cone_follower.py` `along()`: `dist <= 0` returns the first point; `searchsorted(side='right')`; repeated points skipped, including for extrapolation. | `src/saurcon_rl/test/test_cone_follower.py`: boundaries, vertices, end point, extrapolation, repeated points, short-bend and long-bend curvature (now 1/R within 5%), speed limited by a bend ahead. |
| 6 | `capture_map.py` creates `maps/index.csv` with the first grid. In `make_race_video.py`, `map_records()` activates the panel only for rows whose image exists; `path` is always `(N, 4)`; blank cone lines are skipped; the chase camera is optional (onboard-only video). | `scripts/sim_eval/tests/test_make_race_video.py`: non-SLAM run, header-only index, index row without image, grid without trajectory, full panel, no chase camera, the recorded SLAM run, follower waypoints without SLAM. |
| 4 | `full_sim_saurcon.launch.py` `policy_map_origin()`: ArUco gives `0 0 0` (a different origin is rejected); fused SLAM gives `policy_map_origin` (new launch argument, default `-1.127 0 0`). Visual odometry, `fuse_slam:=false` and no localization are rejected at launch. Passed to the node as `map_origin`. | `src/saurcon_rc/test/test_policy_launch.py` (8 tests, including that the value reaches the node command line). |
| 3 | New `src/saurcon_nav/src/map_odom.hpp` (`Pose2`, `mapToOdom`, `PoseHistory`). `spin_cb()` records the global pose each tick and evaluates it at the stamp of the latest `odom -> base_link` by interpolation, so both poses are taken at the same time. The result is stamped `now`. If that stamp falls outside the last 1 s (±30 ms), nothing is published and a warning is logged. There is no blocking wait. | `src/saurcon_nav/test/test_map_odom.cpp` (CTest `map_odom`): the review's 10 m / 9.5 m case, identity under 0–120 ms delivery lag while turning, offset recovery and chain equality at the shared stamp, out-of-order samples, unavailable history, clock reset, angle wrap. |

**Also changed:**
- `scripts/sim_eval/cone_race.sh` is now in the repo; it was previously only in the session scratchpad. It records the chase camera by default and, for the classical follower, `follower.csv`.
- The race video draws the follower's waypoints and lookahead target on the map panel. Without SLAM it shows a top-down track panel placed with ground truth.
- `src/saurcon_rl/README.md` documents the policy pose-source rules.

**Checks run:**

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
PYTHONPATH=src/saurcon_rl:$PYTHONPATH .venv-rl/bin/python -m pytest -q src/saurcon_rl/test scripts/sim_eval/tests  # 46 passed
python3 -m pytest -q src/saurcon_rc/test                                                                       # 8 passed
colcon build --packages-select saurcon_nav saurcon_rc --cmake-args -DBUILD_TESTING=ON
colcon test --packages-select saurcon_nav saurcon_rc && colcon test-result --verbose                           # 4 tests, 0 failures
```

**Simulation runs** (each `scripts/sim_eval/cone_race.sh classical <name> 3 ...`, run after the C++ rebuild):

- **`classical_slam_wp`** (no-marker world, `slam:=true cone_mapping:=rtab`):
  - 3 clean laps: 12.82, 13.33, 12.95 s.
  - The fused global estimator (finding 3 code) logged no `map -> odom` warnings.
  - Cone map: precision 0.55, recall 0.83.
- **`classical_noslam_wp`** (default world):
  - 3 clean laps: 13.04, 12.86, 12.74 s.
  - No `maps/` directory was created, and the video rendered with the track panel.

**Remaining limitations:**

- **Map policy not run end to end.** The map-based RL policy (findings 1 and 4) was not run in Gazebo; that needs a saved RTAB-Map database for localization. Its checks are unit-level.
- **Stops on stale images are now frequent.** Image freshness is judged by capture time, so the cone node stops on "no recent camera image" in 5.9–6.6% of control steps, up from 4–5% before. That is with SLAM load at about 9.5 frames/s, and 12.4 frames/s without SLAM. Each stop is a zero command for one step. That is the safe behaviour, but it costs about 0.3 s per lap. Raising `image_timeout` above 0.3 s, or fixing the camera rate, are the options. Lap times are also slightly slower because finding 5's fix now limits speed for bends correctly.
- **Footprint box.** The footprint note in the cross-check above (box centred on the rear axle) is still open.

## Completion expectations

Implement focused fixes and meaningful regression coverage for these six findings. Preserve unrelated in-progress work. After unit/integration checks, validate the affected paths in isolated simulation, including loss of sensor data and non-SLAM video generation. Report which findings were fixed, the checks actually run, and any remaining limitations. Do not represent the pre-fix passing navigation tests as evidence that autonomous-input failure handling is safe.
