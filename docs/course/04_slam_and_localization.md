# Chapter 4 — SLAM and Localization

**Notebook:** [04_pose_graph_slam.ipynb](notebooks/04_pose_graph_slam.ipynb)

## Learning objectives

- Formulate SLAM as pose-graph optimisation and solve a small one with Gauss–Newton.
- Explain loop closure, why it corrects drift, and how a false closure corrupts a map.
- Set odometry link uncertainty correctly, and explain the difference between incremental and accumulated covariance.
- Separate mapping, localization and global relocalization, and explain the `map → odom` design.

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

## How SAURCON does it

| Concept | Where |
|---|---|
| RTAB-Map parameters, TF odometry variance, `initial_pose` | `src/saurcon_nav/launch/rtabmap_sim.launch.py` |
| Two filter instances, `fuse_slam` | `src/saurcon_rc/launch/full_sim_saurcon.launch.py` (`estimators`) |
| Results and their history | `docs/RTABMAP_STATUS.md` |

## Exercises

1. ★ In the notebook, remove the loop closure and plot how the final pose error grows with lap count.
2. ★★ Add a false closure to the notebook graph. Find the per-link standard deviation above which a 3σ per-link test accepts it.
3. ★★ Explain why `fuse_slam:=true` must turn off RTAB-Map's `publish_tf`. What would `tf2_echo` show otherwise?
4. ★★★ Propose a relocalization guard that works while stationary in a symmetric environment (hint: multiple hypotheses, or wait for motion).
