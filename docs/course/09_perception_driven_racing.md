# Chapter 9 — Perception-Driven Racing: Driving From What the Camera Sees

**Notebook:** [08_cone_perception.ipynb](notebooks/08_cone_perception.ipynb)

## Learning objectives

- Build a classical cone detector from colour, geometry and depth, and choose a ranging method from its error budget.
- Explain *object-level* (abstracted) perception for training, why it is standard practice, and what it assumes.
- Design an observation for a policy that has no map, including short-term memory for a narrow field of view.
- Validate a policy trained on simulated detections against real pixels, and diagnose where a transfer fails.
- Turn a hand-tuned detector model into a measured one: fitting, occlusion, false positives, latency, fine-tuning.
- Build a classical baseline (centreline from cone gates, pure pursuit, curvature speed profile) and compare it honestly with a learned policy.
- Shape a reward for smooth driving, and diagnose a weave from its spectrum rather than from a hunch.
- Train in the full-fidelity simulator when the fast one is not enough, and know what it costs.
- Make a vision-driven controller stop safely when any of its inputs goes stale.

## 1. The problem

Chapter 6's policy drove from a stored track plus a localized pose: a driver with
eyes closed and a perfect map. That fails the moment cones move. Here the car
drives **only from the cones it sees**: no map, no RTAB-Map, no centreline. The
pipeline is

```
camera (colour + depth) ─► cone detector ─► cones in base_link ─► short cone memory ─► policy ─► throttle, steering
                                    ▲ odometry (wheel speed + gyro) moves remembered cones as the car moves
```

The "policy" box has two implementations that take exactly the same input: a
learned PPO policy (sections 3–7, 9–11) and a classical cone follower (section 12).
The classical one turned out to be faster, smoother and more reliable on this
track; section 12.4 discusses why, and when learning would still be worth it.

## 2. The cone detector

`src/saurcon_rl/saurcon_rl/cones.py` (`ConeDetector`) is deliberately classical:
it runs on a Raspberry Pi 4, is explainable, and its errors can be measured.

1. **Colour.** Convert to HSV and threshold the cone colour. Gazebo's cones render
   yellow-orange (hue ≈ 22); the warehouse's rack beams are a deeper orange
   (hue ≈ 7–8) and pallets are dull, so a hue band of 15–32 with high saturation
   and value separates them. MuJoCo's cones render red-orange (hue ≈ 7) and there
   are no racks, so it uses 0–14. Colour bands are parameters, not constants.
2. **Blobs.** Connected components of the mask, after a small closing.
3. **Shape in pixels.** The blob's base must be below the image's horizon row
   ($v > c_y$: cones stand on the floor, below the camera), and the blob must be
   taller than wide.
4. **Range** — three methods, in order of preference:

   | Method | Formula | Measured error (Gazebo) |
   |---|---|---|
   | depth | median of valid depth pixels in the blob | good when present; passive stereo leaves holes on small, plain cones |
   | **ground** | $Z = f_y\,h_\text{cam} / (v_\text{base} + \delta - c_y)$ | 3 cm (< 2 m), 5 cm (2–4 m), 8 cm (4–6.5 m) |
   | size | $Z = f_y\,h_\text{cone} / h_\text{px}$ | ≈ 0.4 m at 2–6.5 m |

   *Ground* assumes a flat floor and a camera at known height $h_\text{cam}$.
   Fitting on Gazebo frames gave $h_\text{cam} = 0.137$ m and a row offset
   $\delta = 1$ px (the blob's bottom row sits about a pixel above the contact).
   *Size* is poor because a cone is only ~8 px tall at 4 m and the colour mask often
   misses its darker base, so one pixel is 12% of the range — and heights read short,
   ranges long.
5. **Shape in metres.** With range known, the blob must be 3–12 cm tall and at most
   7 cm wide, and no farther than 6.5 m (the policy is trained on cones out to 6.5 m).
6. **Position.** Back-project the base pixel at range $Z$ into the optical frame
   ($x$ right, $y$ down, $z$ forward), then transform into `base_link` with the
   camera's mounting transform.

## 3. Training on simulated detections (object-level perception)

Rendering an image every step makes RL training 10–100× slower. Instead, the
training environment (`cone_env.py`) computes what the detector *would* report:

1. Take every cone; express it relative to the camera (0.219 m ahead of `base_link`).
2. Keep those within the field of view (±0.58 rad, slightly inside the 1.204 rad
   lens so a cone straddling the edge is not counted) and 0.35–6.5 m away.
3. Corrupt them like a detector: misses with a range-dependent probability
   (`MISS_PROB`, measured — section 7.1), bearing noise 0.004 rad, range noise
   $2\% \cdot r + \mathcal N(0, 0.006)\,r^2$.
4. Express them in `base_link`.

**Is this standard?** Yes. Separating perception from control and training the
controller on perception *outputs* with an error model is common in robot learning.
The champion-level drone-racing policy "Swift" (Kaufmann et al., *Nature*, 2023) was
trained in simulation on state estimates with perception and dynamics residual
models fitted from real flights, while camera-based perception ran separately;
autonomous-driving planners are routinely developed on object lists; legged robots
are trained on simplified terrain sensing with noise. The approach moves the
sim-to-real question from "do simulated pixels look real?" to "does my detector's
error look like the model?" — which can be measured, and fixed without retraining
the controller.

**What it assumes.** The method is only as good as the detector model. In SAURCON
the first model was *hand-set* from a quick look at errors; its miss rate has since
been measured (section 7.1, first application), while occlusion, false positives,
duplicates and latency are still to do. Section 7 turns each of those into a
procedure.

## 4. The observation and the short cone memory

The policy observes 53 numbers: speed, yaw rate, steering, the previous action, and
the 12 nearest **remembered** cones as (forward, left, present, age).

Why memory: the OAK-D sees ±33°. In the racetrack's 2 m bends the cones the car must
follow are *beside* it, out of view. The first cone policy saw nothing for about a
second mid-bend, held a weak steering angle and ran wide (section 6). `ConeMemory`
keeps every cone detected in the last 2 s:

- stored in a frame that does not move with the car (the world in MuJoCo, `odom`
  on the car), so a remembered cone stays put as the car moves;
- a new detection within 0.3 m of a remembered cone refreshes it (running mean);
- each step, remembered cones are re-expressed in the current `base_link`:
  $p_\text{base} = R^\top(p_\text{odom} - t)$ with $(R, t)$ the current `odom → base_link`.

This is **not a map**: it forgets anything not seen for 2 s, and it never needs
localization, only odometry over a couple of seconds (which drifts millimetres).

**Reward detail: stalling.** With the measured (much higher) miss rate, training
twice converged on *parking*: standing still earns zero reward and never crashes,
which beats driving into cones it cannot see. Stopping below 0.3 m/s for 2 s (after
the first second) now ends the episode with the crash penalty. A per-step time
penalty is the obvious alternative but is worse here: over a 45 s episode it adds up
to more than the crash penalty, so crashing early would look better than driving
carefully. Make the degenerate behaviour exactly as bad as the failure you fear.

**Evaluation detail: keep the detector realistic.** The lap-time evaluation turns
off physics randomisation so runs are comparable. At first it also turned off the
detector's misses and noise, so a policy trained to expect most near and far cones
missing suddenly saw every cone — a situation it had never met — and crashed at the
same spot 8 m in on every evaluation, while its training reward kept rising. With the
detector model left on (`detector_noise=True`), the same checkpoint completed two
clean laps on three seeds. Evaluate under the conditions the policy will face, not
idealised ones.

## 5. Validating on real pixels

Training never sees an image, so validation must. `cone_drive.py` renders MuJoCo's
`oak_rgb` camera (placed and scaled like the OAK-D: $f_x = 465.7$ px at 640×400,
0.137 m above the floor) and its depth every 50 ms, runs the real detector, and drives
the policy from the result. On rendered images the detector placed cones within
1.3 cm RMS and missed 4%; the first cone policy lapped at 10.25 s from pixels against
10.0 s from simulated detections.

MuJoCo is the *easy* case: its depth is a perfect z-buffer, with no stereo noise,
distortion, blur or frame timing. Gazebo's OAK-D model (degraded stereo depth,
15 Hz, warehouse clutter) is the harder check, through the ROS 2 node
`cone_policy_node.py` (section 8).

## 6. Case study — four failures on the way to Gazebo

The first cone policy lapped in MuJoCo but never completed a lap in Gazebo. Each
failure was found by **measuring**, not guessing:

1. **Starved camera.** Gazebo delivered 3–5 Hz instead of 15 Hz while training
   used every core, and requiring an exact colour–depth pair halved it again; the
   policy had fresh input on a third of its steps. *Fix at the time:* use each colour
   image as it arrives with the most recent depth; motion-compensate stored cones with
   odometry; never benchmark while training. (Part of this fix was itself a bug; see
   failure 5.)
2. **Poor ranging.** Gazebo's stereo depth had holes on small cones, so most were
   size-ranged (≈0.4 m error) and the bend looked farther away than it was. *Fix:*
   ground-plane ranging (3–8 cm).
3. **A steering conversion.** Gazebo's Ackermann plugin takes a yaw rate; a test that
   held a yaw-rate command while accelerating showed it converts with the car's
   *actual* speed: $\delta = \arctan(\omega L / v_\text{actual})$, matching to four
   decimals. Commanding $\omega = v_\text{cmd}\tan\delta/L$ therefore over-steered while
   accelerating and under-steered while braking. *Fix:* $\omega = v_\text{measured}\tan\delta/L$.
4. **Blind in the bend — the real cause.** Feeding the policy real Gazebo detections
   and simulated detections for the same instants gave nearly identical actions:
   perception was fine. But from 3.3 s it saw **zero cones** — the bend was outside the
   field of view. *Fix:* the short cone memory (section 4), and retraining.

5. **The fix that caused phantom cones (found later).** The classical follower
   (section 12) ran wide in Gazebo bends while it was perfect in MuJoCo. Its per-step
   debug log (`cone_debug_csv:=`) showed cones in its memory 0.5–1 m *outside* the
   track, only in bends. The colour image was being paired with the *previous* depth
   image, 66 ms older (the depth for the same frame arrives a few ms after the colour).
   While the car turns, the previous frame's depth at a cone's pixel is often floor or
   background behind the cone, so the cone is ranged too far. Failure 1's "most recent
   depth" was the cause. *Fix:* queue each colour image until the depth with **the same
   stamp** arrives (or 0.25 s passes), and look up the odometry pose at the image's own
   stamp too, not the latest one (a 50 ms pose lag at 2 rad/s rotates every cone of the
   frame by 6°). This bug was present in every earlier ROS-stack result in this
   chapter, learned policies included.

**Lessons.** Profile the system (rates, staleness, which ranging method ran) before
explaining it. Test each hypothesis on its own (the steering test). Compare decisions
on real vs simulated inputs to separate perception error from everything else.
And re-check old fixes when new symptoms appear: failure 5 was introduced by the fix
for failure 1, and only a controller with a readable internal state (a planned path
you can plot) made it visible.

## 6a. First results (2026-11-12)

The cone-memory policy, trained 20 M steps in MuJoCo with the measured miss model
and stall termination (`rl_runs/cones_v3`):

| Test | Result |
|---|---|
| MuJoCo, simulated detector (as trained) | clean laps, 21.1 s flying, 4.0 m/s top speed |
| MuJoCo, rendered pixels | crashed after 10 m |
| Gazebo, ROS 2 node, OAK-D model | **one complete lap (~29 s from a standing start)**, then ran wide in the far bend on lap 2 and stopped off the track; 1.2–2.4 m/s |

Two lessons in that table:

- **The detector model now matches Gazebo, not MuJoCo's renderer.** MuJoCo's perfect
  depth lets the real detector miss only ~4% of cones; the policy was trained on the
  25–90% misses measured in Gazebo, so on MuJoCo pixels it again sees more cones than
  it ever has — the same out-of-distribution failure as the evaluation bug, mirrored.
  A policy should be robust to *both*: randomise the detector's miss rate in training
  (e.g. scale `MISS_PROB` by a per-episode factor between 0.1 and 1) — domain
  randomisation applied to perception.
- **Gazebo is the target, and it is closer.** First complete vision-only lap; the
  remaining failure is a bend on lap 2 and low speed. Next steps, in order: miss-rate
  randomisation (above), refit the detector model over several full laps (7.1), add
  occlusion and false positives (7.2–7.3), then retrain and re-race.

## 7. From hand-tuned to measured: the detector-model roadmap

Each step below is a procedure you can run; together they replace guessed numbers
with measured ones.

### 7.1 Fit the error model from logged detections

1. Run laps in Gazebo (or on the real car with motion capture) with the detector and
   ground truth logged at every image (`scripts/sim_eval/logger.py` records frames and
   ground truth; add the detector's output).
2. Associate each detection with the true cone it belongs to (by bearing, then range,
   within a gate). Record: true range $r$, true bearing $\theta$, errors $\Delta r$,
   $\Delta\theta$, and the ranging method used.
3. Fit, as functions of $r$ (and $\theta$ near the image edge):
   bias $\mu(r)$, spread $\sigma(r)$ (a quadratic $a + b r + c r^2$ is usually enough),
   and heavy tails (a Student-*t* or a Gaussian mixture if the residuals demand it).
4. Fit the **miss rate** $p_\text{miss}(r, \theta)$: true visible cones with no
   associated detection, binned by range and bearing (logistic regression works well).
5. Replace the constants in `visible_cones()` with the fitted functions.
6. **Check the fit:** simulate the same laps with the fitted model, and compare
   simulated against real error histograms per range bin (a two-sample
   Kolmogorov–Smirnov test, or simply overlaid histograms and quantile–quantile plots).

**First application (notebook 08, 40 Gazebo frames, ground-plane ranging).**

| Range | Range error, robust std | Miss rate, measured | Miss rate, first hand-set model |
|---|---|---|---|
| 1–2 m | 5 cm | 77% | 6% |
| 2–3 m | 5 cm | 25% | 7% |
| 3–4 m | 6–11 cm | 11% | 9% |
| 4–5 m | 6 cm | 49% | 12% |
| 5–6 m | ~30 cm (few samples) | 85% | 15% |

- *Range error* agreed with the hand-set model out to ~5 m, so it was kept.
- *Misses* did not: near gate cones (the original 1.2 m gates put them at about ±31°,
  at the edge of the ±33° view, or below the image) and far cones (a few pixels tall) are
  missed far more often than assumed. The measured curve (`MISS_PROB` in
  `cone_env.py`) replaced the hand-set one, and the cone-memory policy was retrained
  with it.
- *Association decides the answer.* The first analysis matched detections to true
  cones by bearing only. Along a straight, cones on one side line up at almost the
  same bearing, so far detections were paired with the wrong cone and the "spread"
  came out at 1.2 m at 5 m. Matching on bearing **and** range (within 30%), and
  using a robust spread (1.4826 × median absolute deviation), gave the table above.
- 40 frames from one run is a small, biased sample; refit over several full laps
  (exercise 4) before trusting the numbers on the real car.

### 7.2 Occlusion

A cone behind another cone (or behind a rack) is not seen. In `visible_cones()`,
sort visible cones by range and drop any whose bearing interval
($\pm$ half its width / range) is covered by a nearer cone's interval. For static
obstacles, ray-cast against their footprints (MuJoCo's `mj_ray` does this directly
in the physics model).

### 7.3 False positives and duplicates

From the same logs, count detections that match no cone: rate per image, and where
they appear (range, bearing). In Gazebo they cluster on orange clutter. Add them in
simulation as a Poisson number per image drawn from the fitted spatial distribution;
add duplicates (two detections from one cone) at their measured rate. The cone
memory's merge radius absorbs duplicates; false positives are what the policy must
learn to ignore.

### 7.4 Latency

Measure the delay from image capture (its timestamp) to the detection being used.
In simulation, return detections computed from the car's pose that many control
steps ago (the environment already supports a delay buffer for the state). Odometry
motion compensation removes most of its effect; the model should still include it.

### 7.5 Fine-tune on rendered pixels

After training on simulated detections, continue training for a short period with
MuJoCo rendering the camera and the real detector in the loop (`cone_drive.py`'s
path inside the environment). It is slower — render at 20 Hz for a few hundred
thousand steps — but it catches anything the error model missed.

### 7.6 End-to-end (optional)

Train the policy directly on images (a small CNN encoder), ideally on a GPU with
batched rendering. More general, but far more expensive to train, harder to transfer
from simulation, and heavy for a Pi 4. Use it as a research comparison, not the
first step.

## 8. The track layout, and a hypothesis that was wrong

The learned policies **weaved**: in Gazebo the car swung about ±0.25 m around the
centreline on the straights. A natural hypothesis was that the gates (1.17 m apart
along the track, 1.2 m wide) were so dense that the policy chased individual cones.
The racetrack was regenerated with **2.2 m wide gates** plus **one extra gate between
consecutive gates in each bend** (`add_cone_gates.py --width 2.2 --between 2
--bend-extra 1`: 54 gates, 108 cones; the basement oval keeps its 1.2 m gates).

Wider gates helped visibility (gate cones are no longer at the edge of the view) but
did not remove the weave. Measuring it did settle the question
(`scripts/sim_eval/oscillation_plot.py`): resample the lateral offset on the straights
every 5 cm and take its spectrum. The weave's wavelength was **5–13 m**, not the
1.17 m gate spacing; at 3 m/s that is a 2–4 s period, a slow control oscillation, not
a reaction to individual cones. The policy's steering command also changed by 8.2°
per 50 ms step on average: it was bang-bang steering, smoothed only by the servo.

**Lesson:** turn a visual impression into a measurement before changing the world to
fit a hypothesis. A spectrum distinguishes "reacting to cones" (wavelength = cone
spacing) from "control loop oscillating" (wavelength set by speed and loop delay).

## 9. Training in Gazebo

Exercise 5 of chapter 6 asked how to fine-tune in Gazebo itself. For the cone policy
this was done (`src/saurcon_rl/saurcon_rl/gazebo_cone_env.py`, `train.py --env
gazebo_cones`), because the remaining gap was between MuJoCo's simulated detector
and Gazebo's real one.

- **Lock-step simulation.** Each environment runs its own headless `gz sim` server in
  its own `GZ_PARTITION`, with `real_time_factor` 0, paused. A step is a
  `WorldControl` request with `multi_step` (5 physics steps = 50 ms); the clock topic
  confirms it. The service reply is unreliable, so requests are sent with a 2 ms
  timeout and the clock is the acknowledgement. Without this, waiting for replies
  cost 50 ms–3 s per step.
- **Same perception as the car.** Camera and depth come from Gazebo's sensors through
  gz-transport (no ROS), depth is degraded like the OAK-D's, and the real
  `ConeDetector` and `ConeMemory` run every step.
- **Resets.** The car is teleported (fire-and-forget `set_pose`, verified against
  ground truth) and knocked cones are restored. The memory is in the plugin's
  odometry frame, so a teleport must also clear it: the answer to chapter 6's hint.
- **Latency randomisation:** image age U(0, 100 ms), command delay 0–1 step.
- **Cost.** About **37 steps/s per server**, ~81 steps/s for six servers together;
  an 8 GB GPU holds about six. MuJoCo's simulated detector runs ~1,000 steps/s per
  core: Gazebo training is ~100× slower and suits fine-tuning, not training from
  scratch. Each server is started with `PR_SET_PDEATHSIG` so a crashed trainer
  cannot leave orphan servers (chapter 7).

**Result.** Fine-tuning the MuJoCo policy for ~3 M Gazebo steps (`rl_runs/cones_gz1`)
reached a 23.6 s evaluation lap early and then got *worse*; in the ROS stack it
lapped in 31.75 s with the same 0.5 m weave. Training in the target simulator removes
a modelling gap; it does not fix a reward that pays for bang-bang steering.

## 10. A reward for smooth driving

The progress reward is indifferent to *how* the car steers, and the policy's steering
was limited only by the simulated servo. Three changes (`cone_env.py`):

1. **Servo slew limit** in the environment: the steering target moves at most
   8 rad/s (the MG90S servo's speed), so the policy cannot rely on instantaneous
   steering it will not get on the car.
2. **Steering-rate penalty** $0.5\,\Delta\delta^2$ (normalised steering per step).
3. **Yaw-excess penalty** $0.05\,(r - v\kappa)^2$: yaw rate beyond what the track's
   curvature $\kappa$ at the car's position requires. Turning *for the bend* is free;
   turning more than the bend needs, which is what a weave is, costs.

Retrained from scratch in MuJoCo (`rl_runs/cones_smooth1`): steering change per step
4.2° (was 8.2°), offset standard deviation on the straights 0.093 m (was 0.161 m),
best flying lap 25.25 s. Smoother, but slower than the earlier policy, and the run
was cut short (chapter 7, the `pkill` case study), so it is one seed and not converged.

## 11. Results history (racetrack, cone vision only)

| Controller | Environment | Result |
|---|---|---|
| RL `cones_v3` (1.2 m gates) | Gazebo, ROS | 1 lap (~29 s), then ran wide |
| RL `cones_v3` | Gazebo, 2.2 m gates | failed |
| RL `cones_v4_wide` (MuJoCo fine-tune on 2.2 m gates) | MuJoCo, simulated detector | 10/10 seeds, ~22.5 s |
| RL `cones_v4_wide` | Gazebo, ROS | 2 laps, 31.8 s |
| RL `cones_gz1` (Gazebo fine-tune) | Gazebo, ROS | 1 lap, 31.75 s, weave ~0.5 m |
| RL `cones_smooth1` (smooth reward) | MuJoCo, simulated detector | 25.25 s flying, half the steering activity |
| **Classical follower** | MuJoCo, rendered pixels | 11.85 s flying |
| **Classical follower** | MuJoCo, simulated detector | 8/8 seeds clean |
| **Classical follower** | Gazebo lock-step, 30% of frames dropped | 5/5 clean |
| **Classical follower** | Gazebo, ROS | 3 laps, 11.7–13.3 s; offset std 0.04 m |
| **Classical follower** + RTAB-Map running | Gazebo, ROS, no ArUco markers | 3–4 clean laps, 12.4–13.3 s (earlier, 1 of 3 runs clean; see 12.3) |

The RL results were all obtained before the depth-pairing fix (failure 5); they have
not been re-run since, so part of the gap may close.

## 12. A classical baseline: the cone follower

`src/saurcon_rl/saurcon_rl/cone_follower.py` takes **exactly the policy's input**:
the cone memory in `base_link` and the measured speed. No map, no localization, no
learning.

### 12.1 The algorithm

1. **Centreline points from Delaunay edges.** Triangulate the remembered cones. An
   edge between the two cones of a gate, or a diagonal to the next gate on the other
   side, is 2.2–2.5 m long; an edge along one boundary is much shorter. Midpoints of
   edges **1.95–2.75 m** long are therefore points on the centreline. (The lower
   bound matters: the inner cone rows of the two straights are 1.8 m apart and must
   not be paired, or midpoints appear in the infield.)
2. **Chain them.** From the rear axle, repeatedly take the nearest midpoint
   0.15–2.5 m ahead within 70° of the current heading (cost $r + 1.5\,|\Delta\psi|$).
   The edge a midpoint came from must **cross** the direction of travel (within 50°
   of perpendicular); this rejects an edge between two cones on the same boundary
   whose neighbours were missed, which would otherwise look like a gate.
3. **Single-boundary fallback.** In bends the camera (±33°) often sees only the outer
   cones. If the chain is shorter than 1 m, chain the cones of one boundary and offset
   them by half the track width towards the car; drive at most 2.5 m/s on it.
4. **Pure pursuit** from the rear axle: $\delta = \arctan(2L\sin\alpha/\ell_d)$, with
   the lookahead $\ell_d = 0.7 + 0.3\,v$ m (≤ 2.2 m) measured along the path, from the
   pose predicted 50 ms ahead (the measured sensing-to-actuation delay).
5. **Speed.** The tightest curvature $\kappa$ on the path ahead (circles through points
   0.4 m apart) sets $v = \sqrt{a_\text{lat}/\kappa}$ with $a_\text{lat} = 5$ m/s²
   (half the grip); braking at 2.5 m/s² bounds the approach; the car must be able to
   stop within the path it can see; the steering angle caps speed through
   $v^2 \tan\delta / L \le a_\text{lat}$. If no path is found it holds the last
   command and slows, and stops after 1 s.

### 12.2 Building it — four failures, each measured

| Symptom | Cause | Fix |
|---|---|---|
| Path wandered into the infield | inner rows of the two straights 1.8 m apart, paired as a "gate" | edge window 1.95–2.75 m |
| Path jumped onto a boundary | two cones of one side with the cones between them missed | edge must cross the direction of travel |
| Ran wide on bend exits | only outer cones visible, no gate | single-boundary fallback |
| Overran the first bend | the bend is seen late; braking planned at the car's limit | plan braking at 2.5 m/s², 5 m/s cap |

### 12.3 Two bugs found in review

A review of the branch (`docs/branch_review_handoff.md`) found, among others:

- **The speed planner was blind to short bends.** `along(path, 0)` used
  `searchsorted(s, 0) - 1 = -1`, i.e. the *last* path segment, and returned a point
  near the end of the path. Every curvature estimate starts at distance 0, so for a
  short path (typical when entering a bend) the "tightest curvature" came out at
  0.013 /m instead of ~1.7 /m. The car was slowed only by its other limits. The fix is
  one line; the regression test bends a short path and checks $\kappa \approx 1/R$.
  It plausibly explains part of the bend run-wides under SLAM load (12.4).
- **Stale inputs did not stop the car** — section 13.

### 12.4 Why the classical follower won here, and when RL still makes sense

On this track the classical follower lapped about twice as fast as any learned
policy, with a tenth of the weave, and transferred from MuJoCo to Gazebo without
tuning. The reasons are worth stating precisely:

- **The structure is known.** "The centreline is the midpoint of each gate" is the
  whole task; the follower is told it, while the policy must discover it from 12
  noisy points and a progress reward, and can find degenerate solutions (parking,
  weaving) on the way.
- **It is inspectable.** Its planned path can be plotted on every frame; that is how
  failure 5 (phantom cones) was found. A policy's mistake shows up only as behaviour.
- **It degrades gracefully.** Dropping 30% of frames in lock-step Gazebo changed
  nothing; the learned policies were sensitive to the detector's miss rate (6a).

Learning earns its place when the structure is *not* known or the limit is in the
dynamics: driving at the grip limit, using the full track width, recovering from
slides, or situations the hand-written rules do not cover. A strong approach is to
combine them — the classical path as the policy's observation, or RL tuning the
classical controller's parameters, or a residual policy on top of pure pursuit —
and always to keep the classical controller as the baseline every learned result is
compared against.

### 12.5 Running it with SLAM

The follower needs no map, but it runs fine with RTAB-Map mapping in parallel
(`slam:=true cone_mapping:=rtab`, no-marker world): chapter 4 shows the occupancy grid
and cone map it builds. RTAB-Map's CPU load cut the camera from ~12 to 9.5–11 frames/s;
before the curvature and stale-input fixes, only 1 of 3 such runs was clean, the others
running wide in a bend on lap 2 or 3. After the fixes, two SLAM runs were clean
(3 laps each, 12.4–13.3 s); that is still a small sample.

Race videos (`scripts/sim_eval/make_race_video.py`) show the onboard camera with
detections, a chase camera, and a top-down panel with the follower's **waypoints**
(the chained midpoints, magenta) and lookahead target (red ring), on the live
RTAB-Map grid or, for a run without SLAM, on a saved grid (`--map-from`).

## 13. Stopping on stale inputs

The state machine stops the car if `/auto_cmd` stops arriving for 0.25 s (chapter 5).
That does **not** protect against a node that keeps publishing confident commands
computed from stale data. The review reproduced exactly that: with a fresh camera
image and an odometry transform 99 s old, the cone node published full speed,
because it clamped the transform's age to 0.2 s and substituted an identity pose if
the lookup failed.

`cone_policy_node.py` now drives only when **all** inputs are fresh, and otherwise
publishes a zero command and resets its command history:

| Input | Required | Note |
|---|---|---|
| camera image | captured (header stamp) within `image_timeout` = 0.3 s | late *processing* of an old image does not renew it |
| odometry (`/saurcon/odom_nav`) | stamped within `odom_timeout` = 0.25 s, newer than the last | speed and yaw rate come from it |
| `odom → base_link` TF | no older than `tf_timeout` = 0.25 s; lookup must succeed | missing/expired also clears the cone memory, whose positions are in `odom` |
| fallback pose for an image | within `tf_fallback_max` = 0.1 s of the image stamp | otherwise the image is dropped |

Normal latency (a pose 50–100 ms old) is still extrapolated with the measured speed
and yaw rate. Under SLAM load these rules stop the car for one control step on about
6% of steps, a visible but safe cost. The rules are tested with a fake clock, TF
buffer, policy and publisher (`src/saurcon_rl/test/test_input_watchdogs.py`), for both
the classical and the learned path — exercise 7.

## How SAURCON does it

| Concept | Where |
|---|---|
| Detector, cone map, scoring | `src/saurcon_rl/saurcon_rl/cones.py` |
| Simulated detector, cone memory, observation, smooth reward, environment | `src/saurcon_rl/saurcon_rl/cone_env.py` |
| Gazebo lock-step training environment | `src/saurcon_rl/saurcon_rl/gazebo_cone_env.py`, `train.py --env gazebo_cones` |
| Classical cone follower | `src/saurcon_rl/saurcon_rl/cone_follower.py` |
| Driving from rendered MuJoCo pixels (policy or `--model classical`) | `src/saurcon_rl/saurcon_rl/cone_drive.py` |
| ROS 2 cone node (camera in, `/auto_cmd` out; `model:=classical`) | `src/saurcon_rl/saurcon_rl/cone_policy_node.py`, launch `cone_policy_model:=` |
| Cone mapping with truth or RTAB-Map poses (Gazebo) | `src/saurcon_rl/saurcon_rl/cone_mapper_node.py`, launch `cone_mapping:=` |
| Track layout (gate width, bend gates) | `src/middle_earth/scripts/add_cone_gates.py` |
| Gazebo race harness and videos | `scripts/sim_eval/cone_race.sh`, `scripts/sim_eval/make_race_video.py` |
| Weave analysis | `scripts/sim_eval/oscillation_plot.py` |
| Tests | `src/saurcon_rl/test/` |
| Training | `python -m saurcon_rl.train --env mujoco_cones` (or `gazebo_cones`) |

```bash
# Classical follower in Gazebo, 3 laps, with RTAB-Map mapping and no ArUco markers
scripts/sim_eval/cone_race.sh classical classical_slam 3 \
    world:=$PWD/evaluation/worlds/no_markers.world slam:=true cone_mapping:=rtab
.venv-rl/bin/python scripts/sim_eval/make_race_video.py evaluation/cones_gz/classical_slam out.mp4
# The same follower in MuJoCo, from rendered pixels
.venv-rl/bin/python -m saurcon_rl.cone_drive --model classical --laps 2 --video classical_mujoco.mp4
```

## Exercises

1. ★ Derive the ground-plane range error for a one-pixel error in $v_\text{base}$ at 2, 4 and 6 m with $h_\text{cam} = 0.137$ m. Compare with the size method.
2. ★ In notebook 08, set the memory horizon to 0 and drive the scripted bend. How many cones does the observation contain mid-bend?
3. ★★ Implement section 7.2's occlusion in `visible_cones()` and measure how many detections it removes on a lap.
4. ★★ Carry out section 7.1 on a Gazebo lap: fit $\sigma(r)$ and $p_\text{miss}(r)$, and compare with the hand-set values.
5. ★★★ Implement section 7.5 and report whether lap time or robustness changes.
6. ★★★ Build the cone corridor from the *Gazebo cone map* (chapter's mapper node) and compare a map-based policy with the memory-only policy on a rearranged course.
7. ★ Read `test_input_watchdogs.py`. Add a test that a cone node whose odometry *clock jumps backwards* (simulation reset) recovers once fresh data arrives.
8. ★★ Run `oscillation_plot.py` on a classical-follower run and on an RL run. Where are the spectral peaks, and what sets them?
9. ★★ The follower's lateral acceleration budget is 5 m/s² against ~10 m/s² of grip. Raise it step by step in MuJoCo; where does it start to fail, and why there?
10. ★★ Make the follower's path the observation of an RL policy (replacing the 12 cones) and compare its learning curve with the cone-based policy's.
11. ★★★ Train a residual policy that adds a steering and speed correction to the classical follower's command. Does it beat the follower on lap time without losing its robustness?
