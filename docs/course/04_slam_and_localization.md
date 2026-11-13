# Chapter 4 — SLAM and Localization

**Notebook:** [04_pose_graph_slam.ipynb](notebooks/04_pose_graph_slam.ipynb)

## Learning objectives

- Formulate SLAM as pose-graph optimisation and solve a small one with Gauss–Newton.
- Explain loop closure, why it corrects drift, and how a false closure corrupts a map.
- Set odometry link uncertainty correctly, and explain the difference between incremental and accumulated covariance.
- Separate mapping, localization and global relocalization, and explain the `map → odom` design.
- Compose transforms at a common timestamp, and explain the error from mixing instants.
- Configure an occupancy grid so free space is actually observed, and explain why mapped landmarks duplicate after loop closures.

## 1. SLAM as a graph

Each time the car moves enough, RTAB-Map stores a **node**: the pose estimate plus
the camera image, depth and visual features. **Edges** constrain pairs of nodes:

- *odometry links* between consecutive nodes, from the odometry filter;
- *loop-closure links* when the current image matches an earlier node, from visual
  feature matching plus PnP-style registration.

Each edge carries a relative pose measurement $\mathbf z_{ij}$ and an information
matrix $\Omega_{ij} = \Sigma_{ij}^{-1}$. SLAM finds the node poses minimising

$$\sum_{(i,j)} \mathbf e_{ij}^\top \Omega_{ij}\, \mathbf e_{ij}, \qquad
\mathbf e_{ij} = \mathbf z_{ij} \ominus (\mathbf x_i^{-1} \oplus \mathbf x_j).$$

Gauss–Newton linearises the errors, solves $H\Delta = -\mathbf b$ for all poses at
once, and iterates. Odometry alone gives a chain whose error grows without bound;
one loop closure adds a cycle that spreads the accumulated error around the loop.
RTAB-Map's back end is g2o (selected in `rtabmap_sim.launch.py`).

## 2. Accepting or rejecting a loop closure

Visual matches can be wrong, especially in repetitive environments: SAURCON's
warehouse has two long aisles that look identical in opposite directions. A wrong
closure, once optimised, drags the whole map. RTAB-Map's check
(`RGBD/OptimizeMaxError`) re-optimises with the candidate and rejects it if any
link's error exceeds $k$ standard deviations of that link.

This only works if the link standard deviations are **right**.

## 3. Case study — accumulated vs. incremental covariance

RTAB-Map treats the covariance in each odometry message as the uncertainty of
*one link* between nodes. SAURCON's filter published its **total** covariance,
which grows for the whole run — metres after a few minutes. So by 139 s RTAB-Map
believed each 0.5 m link could be off by metres, and accepted a closure that
matched the y=4 aisle (driving +x on a reverse lap) to the y=0 aisle. The map
jumped 4 m sideways (RMS error 2.3 m).

Switching RTAB-Map to read odometry from TF with a fixed per-link variance fixed
the model of uncertainty, but 2 cm per link still let the closure through: the 4 m
error was spread over ~160 links (about 2.5 cm each). The measured drift was under
1 cm per link, so the variance was set to 5 mm and 0.18°. The false closure then
failed the test, 114 bad matches were rejected, and the two-direction map came out
at 0.11 m RMS.

**Lesson:** a probabilistic check is only as good as the uncertainties you give it.
"Conservative" (too large) noise is not safe — it disables outlier rejection.

## 4. Mapping, localization and relocalization

- **Mapping** (`Mem/IncrementalMemory=true`) adds nodes and closures.
- **Localization** (`false`) matches the current view against a saved map without
  adding nodes, and publishes `/rtabmap/localization_pose`.
- **Global relocalization** is localization from an unknown pose. In a symmetric
  environment it is ambiguous. SAURCON parked facing −x relocalized to a look-alike
  place 5 m away facing +x; RTAB-Map's guard (checking a localization against
  several recent odometry nodes) cannot work while the car is not moving. Giving a
  known start pose (`initial_pose:=`) avoids this, as does a real deployment
  restarting where it last stopped.

## 5. Who owns `map → odom`? The dual-filter design

RTAB-Map needs smooth odometry that it can trust between nodes; the car's
controller needs a globally correct pose at high rate. One filter cannot do both
without a feedback loop (RTAB-Map's corrections would come back to it as
"odometry"). SAURCON runs **two instances of the same UKF**:

1. **Odometry UKF**: wheel + gyro only; publishes `odom → base_link`. RTAB-Map
   uses it and it never sees RTAB-Map's corrections.
2. **Global UKF**: the same prediction plus RTAB-Map's pose as a measurement
   (latency-compensated, chapter 3); publishes `/saurcon/nav_state` at 50 Hz and
   `map → odom`. RTAB-Map's own `map → odom` publishing is switched off.

While mapping, RTAB-Map publishes no localization pose, so the global filter uses
the newest node of the optimised path (`/rtabmap/mapPath`) instead.

Result in the marker-free world (two laps): fused UKF 0.070 m RMS, RTAB-Map alone
0.069 m, odometry alone 0.168 m — the fused filter matches RTAB-Map's accuracy at
25× its rate.

### Case study — combining poses from two different instants

The global filter computes `map → odom` as
$T_{\text{map}\to\text{odom}} = T_{\text{map}\to\text{base}} \oplus T_{\text{odom}\to\text{base}}^{-1}$.
Its own pose is for `now`; the newest `odom → base_link` transform is usually a few
tens of milliseconds older. The original code combined the two anyway. With
*perfect* estimates — global x = 10 m at t = 2.0 s, odometry x = 9.5 m at t = 1.9 s
(5 m/s) — it published a 0.5 m correction, and once odometry for t = 2.0 s arrived,
`map → odom → base_link` put the car at 10.5 m. The error is the car's motion during
the lag, built into the correction.

The fix keeps one second of the global filter's poses and evaluates them, by
interpolation, **at the odometry transform's stamp**; only then are the two composed
(`src/saurcon_nav/src/map_odom.hpp`). If that stamp is outside the history, nothing
is published that tick rather than something wrong. The test
(`test/test_map_odom.cpp`) drives identical global and odometry trajectories through
a turn with 0–120 ms of delivery lag and checks the correction stays the identity.
**Lesson:** every composition of transforms needs all its terms at one instant —
check the timestamps, not just the frames.

## 6. The occupancy grid

Besides the pose graph, RTAB-Map builds a 2-D **occupancy grid** (`/map`, 5 cm
cells) from the depth image at each node: each cell is *free*, *occupied* or
*unknown*. How much of it gets filled depends on settings that are easy to overlook.

**Case study — why the map stayed grey.** After four laps, half of the area inside the
track was still unknown. Three causes:

1. **No ray tracing.** With `Grid/RayTracing` off (the default), a cell is marked free
   only where floor points landed. The OAK-D sits 14 cm above the floor, so it sees
   the floor at a grazing angle and few points land on it. With ray tracing, every
   depth ray also clears the cells between the camera and what it hit.
2. **Range.** `Grid/RangeMax` = 4 m ignores everything farther.
3. **The same view every lap.** A forward camera (±33°) on the racing line sees the
   same things each lap; more laps add almost nothing.

Turning on ray tracing and marking the car's own footprint free
(`Grid/FootprintLength/Width/Height`, `GridGlobal/FootprintRadius`) cut the unknown
area inside the track from **49% to 11–14%**. The cost: RTAB-Map's extra CPU load
dropped the cone node's camera rate from 11.0 to about 9.5 frames/s. Behind racks and
pallets stays unknown, because no ray reaches it from the racing line; filling that
needs driving another route. On real stereo depth, ray tracing also traces through
noisy pixels, so validate it on the car before relying on it.

## 7. Mapping objects: the cone map and its duplicates

`cone_mapper_node.py` (`cone_mapping:=rtab`) places each detected cone in the map
frame with RTAB-Map's pose at the time it was seen, and merges detections within a
radius. Against the true cones: recall 0.83–0.87, position error 7.5–9.6 cm RMS, but
**precision only 0.47–0.57** — about one mapped cone in two is a duplicate. Each cone
is fixed once placed, but a later loop closure corrects the *poses* it was placed
from, so the next sighting of the same cone lands a few centimetres to decimetres
away and becomes a new cone. The general fix is to attach landmarks to the graph node
they were seen from, so they move with every optimisation, or to add them to the
graph as landmarks (exercise 5).

## How SAURCON does it

| Concept | Where |
|---|---|
| RTAB-Map parameters, TF odometry variance, `initial_pose`, grid settings | `src/saurcon_nav/launch/rtabmap_sim.launch.py` |
| Two filter instances, `fuse_slam` | `src/saurcon_rc/launch/full_sim_saurcon.launch.py` (`estimators`) |
| `map → odom` at a common time | `src/saurcon_nav/src/map_odom.hpp`, `state_estimator_node.cpp` (`spin_cb`) |
| Cone map from RTAB-Map poses | `src/saurcon_rl/saurcon_rl/cone_mapper_node.py` |
| Map snapshots and race videos with the map | `scripts/sim_eval/capture_map.py`, `scripts/sim_eval/make_race_video.py` |
| Results and their history | `docs/RTABMAP_STATUS.md` |

## Exercises

1. ★ In the notebook, remove the loop closure and plot how the final pose error grows with lap count.
2. ★★ Add a false closure to the notebook graph. Find the per-link standard deviation above which a 3σ per-link test accepts it.
3. ★★ Explain why `fuse_slam:=true` must turn off RTAB-Map's `publish_tf`. What would `tf2_echo` show otherwise?
4. ★★★ Propose a relocalization guard that works while stationary in a symmetric environment (hint: multiple hypotheses, or wait for motion).
5. ★★★ Store each mapped cone relative to the RTAB-Map node it was first seen from, and re-place all cones whenever `/rtabmap/mapPath` changes. Measure the cone map's precision before and after.
6. ★★ Map the track with `Grid/RayTracing` on and off and with `Grid/RangeMax` 4, 6 and 8 m. Report the unknown fraction inside the track and the camera rate the cone node achieves in each case.
7. ★ Using the case study in section 5, compute the `map → odom` error from mixing timestamps for a car at 5 m/s with 40 ms of odometry lag.
