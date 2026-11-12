# Chapter 9 — Perception-Driven Racing: Driving From What the Camera Sees

**Notebook:** [08_cone_perception.ipynb](notebooks/08_cone_perception.ipynb)

## Learning objectives

- Build a classical cone detector from colour, geometry and depth, and choose a ranging method from its error budget.
- Explain *object-level* (abstracted) perception for training, why it is standard practice, and what it assumes.
- Design an observation for a policy that has no map, including short-term memory for a narrow field of view.
- Validate a policy trained on simulated detections against real pixels, and diagnose where a transfer fails.
- Turn a hand-tuned detector model into a measured one: fitting, occlusion, false positives, latency, fine-tuning.

## 1. The problem

Chapter 6's policy drove from a stored track plus a localized pose: a driver with
eyes closed and a perfect map. That fails the moment cones move. Here the car
drives **only from the cones it sees**: no map, no RTAB-Map, no centreline. The
pipeline is

```
camera (colour + depth) ─► cone detector ─► cones in base_link ─► short cone memory ─► policy ─► throttle, steering
                                    ▲ odometry (wheel speed + gyro) moves remembered cones as the car moves
```

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
   policy had fresh input on a third of its steps. *Fix:* use each colour image as it
   arrives with the most recent depth; motion-compensate stored cones with odometry;
   never benchmark while training.
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

**Lessons.** Profile the system (rates, staleness, which ranging method ran) before
explaining it. Test each hypothesis on its own (the steering test). Compare decisions
on real vs simulated inputs to separate perception error from everything else.

## 6a. Results so far (2026-11-12)

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
- *Misses* did not: near gate cones (the 1.2 m gates put them at about ±31°, at the
  edge of the ±33° view, or below the image) and far cones (a few pixels tall) are
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

## How SAURCON does it

| Concept | Where |
|---|---|
| Detector, cone map, scoring | `src/saurcon_rl/saurcon_rl/cones.py` |
| Simulated detector, cone memory, observation, environment | `src/saurcon_rl/saurcon_rl/cone_env.py` |
| Driving from rendered MuJoCo pixels | `src/saurcon_rl/saurcon_rl/cone_drive.py` |
| ROS 2 cone policy (camera in, `/auto_cmd` out) | `src/saurcon_rl/saurcon_rl/cone_policy_node.py`, launch `cone_policy_model:=` |
| Cone mapping with truth or RTAB-Map poses (Gazebo) | `src/saurcon_rl/saurcon_rl/cone_mapper_node.py`, launch `cone_mapping:=` |
| Training | `python -m saurcon_rl.train --env mujoco_cones` |

## Exercises

1. ★ Derive the ground-plane range error for a one-pixel error in $v_\text{base}$ at 2, 4 and 6 m with $h_\text{cam} = 0.137$ m. Compare with the size method.
2. ★ In notebook 08, set the memory horizon to 0 and drive the scripted bend. How many cones does the observation contain mid-bend?
3. ★★ Implement section 7.2's occlusion in `visible_cones()` and measure how many detections it removes on a lap.
4. ★★ Carry out section 7.1 on a Gazebo lap: fit $\sigma(r)$ and $p_\text{miss}(r)$, and compare with the hand-set values.
5. ★★★ Implement section 7.5 and report whether lap time or robustness changes.
6. ★★★ Build the cone corridor from the *Gazebo cone map* (chapter's mapper node) and compare a map-based policy with the memory-only policy on a rearranged course.
