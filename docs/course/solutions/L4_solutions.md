# Lecture 4 — Solutions

### 4.1 [C] Error growth without loop closure

**Expected result.** Notebook 04's odometry has a heading bias, so dead reckoning ends 5.27 m off after
two laps, and the optimised graph with a closure is at 0.245 m RMS against 2.50 m for odometry
(cells 4–6). Without the closure, the final error grows **quadratically** in distance (log–log slope ≈ 2):
a constant heading-rate error $\dot\epsilon$ gives heading error $\dot\epsilon t$ and lateral error
$\int v\,\dot\epsilon t\,dt = \tfrac12 v\dot\epsilon t^2$. For comparison, white heading noise gives
slope 1.5 (an integrated random walk) and white translation noise gives 0.5. On a closed loop the
error is periodic in part, because a heading bias rotates the whole lap, so fit on lap *end points*.
Rubric: plot (3), fitted exponent (3), mechanism (4).

### 4.2 [T] Per-link threshold

See the lecture's answer: $\sigma < D/(kN) = 8.3$ mm. Full credit also states the assumption (even
spreading) and its direction: the optimiser spreads error in proportion to link *variance*, so a few
loose links (larger σ) absorb more and make the false closure *easier* to accept.

### 4.3 [T] One publisher per TF edge

With `fuse_slam:=true`, the global UKF publishes `map → odom`. If RTAB-Map also published it, the edge
would have two publishers with different values. tf2 interpolates between the most recent messages
regardless of source, so `tf2_echo map base_link` would show the pose **jumping back and forth** between
RTAB-Map's correction and the UKF's at the combined publishing rate (jitter of up to the two estimates'
disagreement, decimetres after a loop closure), and consumers would see an inconsistent tree. tf2 may
also warn about `TF_REPEATED_DATA`. A worse failure is that RTAB-Map's correction would feed back
through `map → base_link` into the global filter's measurement path. Rubric: two publishers (3), the
observable symptom (4), the feedback consequence (3).

### 4.4 [T] Stationary relocalization in a symmetric environment

**Model answer.** Keep **multiple hypotheses** rather than committing to the best visual match.
Place recognition returns candidate poses $\{\mathbf x^{(j)}\}$ with match likelihoods $\ell_j$.
Maintain them (a particle set or a mixture of Gaussians), propagate all with odometry, and update each
with every new frame. **Commit** to hypothesis $j$ only when its posterior ratio over the runner-up
exceeds a threshold $\Lambda$; until then, report "not localized" and keep the planner on
odometry-only behaviour (the cone follower needs nothing more).

**Failure probability.** With $M$ indistinguishable places and no prior, a system forced to commit
while stationary is wrong with probability $(M-1)/M$; no stationary data can do better, because the
views are identical by assumption. With the commit rule, an error requires a wrong hypothesis to
exceed $\Lambda$ times the right one's likelihood, which is bounded by about $1/(1+\Lambda)$ per
decision under the test's assumptions, at the cost of waiting for motion. Breaking the symmetry needs
new information: motion (the hypotheses predict different views after the car moves), a prior (where
it parked last), or a wider view (rotating the sensor). Strong answers note that SAURCON's
`initial_pose` is exactly a prior.

### 4.5 [T] Mixing instants

See the lecture's answer. Combined with an unknown direction, the error is between
$|0.2 - 0.24|$ and $0.2 + 0.24$ m, so up to **0.44 m** at a point 3 m from the car.

### 4.6 [C] Cones that move with the graph

**Method.** For each cone, store the id of the node it was first seen from and its position in that
node's frame (averaging further sightings in the same node frame). On every `/rtabmap/mapPath` update,
recompute map positions as ${}^{M}T_{\text{node}}\,\mathbf p_\text{node}$, then merge cones closer than
the merge radius.

**Expected result.** Precision rises from the 0.47–0.74 measured in the lecture toward ≥ 0.85, with
recall unchanged (0.83–0.87). Residual duplicates come from cones first seen at long range (ranging
error larger than the merge radius). Require three runs and an interval, since precision varies
±0.1 between runs. Rubric: implementation (4), measurement over runs (3), analysis of residuals (3).

### 4.7 [S] Ray tracing and range

**Reference measurements** (feature warehouse, 3–4 laps): unknown area inside the track **49%** without
ray tracing and **11–14%** with it plus footprint clearing; the cone node's camera rate fell from 11.0
to about 9.5 frames/s. Expect a further 2–5 points of unknown area removed at 6–8 m range, a higher CPU
cost, and spurious free space through noisy far depth on a real sensor. A strong answer chooses
explicitly, for example "ray tracing on, range 6 m in simulation, 4 m on the car", and names the
deciding metric: the planner's stale-step rate, not map completeness.

### 4.8 [T] A cone in the middle of the lane

**Prediction.** `drivable_grid` keeps cones whose lateral offset from the driven path is 0.5–1.8 m. A
cone at the lane centre (offset ≈ 0) is **ignored as a boundary**, so the corridor is unchanged. The
cone itself is ~7 cm tall, above `Grid/MaxGroundHeight` = 3 cm, so RTAB-Map marks it occupied, and
`keep_obstacles` keeps that cell blocked inside an otherwise open corridor. A cone placed at 0.6 m
offset is different: it is taken as a boundary cone, and the median width over ±1 m shifts by an amount
that depends on how many true boundary cones share the window, so the corridor narrows locally.

**A better rule.** Fit each boundary locally (a line or circle through the cones within ±1.5 m along
the path) and classify a cone as an **obstacle** if its residual from its side's boundary exceeds
0.3 m while that side already has well-fitting cones nearby. Mark obstacles as blocked discs of the
cone radius plus the car's half-width. Test it in `test_map_cleaner.py`'s stadium geometry with cones
at offsets 0, 0.3, 0.6 and 0.9 m. Rubric: correct prediction for both offsets (4), rule (4), test (2).
