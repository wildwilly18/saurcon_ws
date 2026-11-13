# Lecture 9 — Solutions

### 9.1 [T] Ranging sensitivity

Reference script, $f_y = 465.7$ px:

| Range | Ground plane, per pixel | Size, per pixel |
|---|---|---|
| 2 m | 6.3 cm | 12.1 cm |
| 4 m | 25.1 cm | 48.4 cm |
| 6 m | 56.4 cm | 108.9 cm |

The ratio is constant at $h/h_\text{cone} = 1.93$: the lever arm. Measured ground-plane errors (3–8 cm)
are well under one pixel's worth beyond 2 m, because the base row is located consistently to sub-pixel
accuracy. Size ranging adds a systematic bias (missed dark base, heights short, ranges long), which no
amount of averaging removes.

### 9.2 [T] Pure-pursuit curvature

See the lecture's answer. An alternative route: the chord from the rear axle to the target subtends
angle $2\alpha$ at the circle's centre (the tangent–chord angle equals half the subtended arc), so
$\ell_d = 2\rho\sin\alpha$.

### 9.3 [C] Memory horizon 0

**Reference result** (notebook 08's bend drive, 20 seeds; mean remembered cones within 2 m of the car,
mid-bend):

| Horizon | Cones within 2 m, mid-bend |
|---|---|
| 0 s | **0.2** (0.1–0.5 over seeds) |
| 0.5 s | 1.7 |
| 1 s | 3.3 |
| 2 s | 7.0 (5.9–8.4) |

With no memory the observation is almost empty for most of the bend: the "blind in the bend" failure of
§4, failure 4. The count grows roughly linearly with the horizon until it saturates at the number of
cones beside the car.

### 9.4 [C] Detector-model fit over a full lap

Rubric only (data-dependent). Required: association on bearing **and** range (§3); robust spread
(1.4826 × MAD) with bootstrap confidence bands per range bin; miss probability by bin with
Clopper–Pearson intervals (7.1); comparison against `MISS_PROB` with a two-sample test or overlaid
histograms; and a statement of which bins have too few samples. Reference values from 40 frames
(notebook 08): miss rates 0.77 (1–2 m), 0.25 (2–3 m), 0.11 (3–4 m), 0.49 (4–5 m), 0.85 (5–6 m); range
spread 5–11 cm to 5 m. A full lap on the 2.2 m gates should show *lower* near-range misses than the
40-frame sample (gate cones are no longer at the edge of the view).

### 9.5 [T] Delaunay edge lengths

See the lecture's answer and the reference script: at $s = 0.65$ m, chords with $k = 3$ (1.95 m) and
$k = 4$ (2.60 m) fall in the window; at $s = 1.17$ m, $k = 2$ (2.34 m) does. Full credit adds the
consequence: chords enter the window only when $k - 1$ consecutive cones are missed, so their frequency
scales with the miss rate to the power $k - 1$. At a 25% miss rate a $k = 2$ chord (racetrack) needs one
miss (≈ 25% of the time), and a $k = 3$ chord (feature warehouse) needs two (≈ 6%); but the warehouse
has twice as many cone pairs per metre and tighter bends, where the crossing test was weakest.

### 9.6 [C] Weave spectra

**Expected result.** Learned policies in MuJoCo and Gazebo show a broad peak at a wavelength of 5–13 m
(a 2–4 s loop oscillation at 3 m/s; Lecture 9 §5). The classical follower shows no dominant peak, and
its offset standard deviation on straights is ≈ 0.04 m. What sets a peak: speed × loop period, where the
period comes from lookahead, actuation lag and delay; *not* the cone spacing (1.17 m on the racetrack),
which would appear as a sharp line if the controller reacted to individual cones.

### 9.7 [C] Raising the lateral-acceleration budget

**Reference result** (reference script; MuJoCo, simulated detector, racetrack, 2 laps, 3 seeds; lap times
in seconds):

| $a_\text{lat}$ | Seed 0 | Seed 1 | Seed 2 | Max lateral offset |
|---|---|---|---|---|
| 5 m/s² (default) | 12.45, 12.15 | 13.4, 12.3 | 13.4, 13.2 | 0.23 m |
| 7 m/s² | 12.1, 11.3 | 12.4, 11.6 | 12.9, 11.65 | 0.22 m |
| 10 m/s² | 11.65, 11.1 | 11.95, 10.95 | 12.7, 11.85 | 0.58 m |

**Teaching note.** No run failed, even at the grip limit, and doubling the budget saves only about
1 s per lap (≈ 8–10%: mean second lap 12.55 s at 5 m/s², 11.30 s at 10 m/s²). The follower is **perception-limited, not grip-limited**: in (9.3) the stop-within-sight
term $\sqrt{2b(\ell_\text{path}-0.3)}$ and the 5 m/s cap bind on most of the lap, because the camera sees
only 5–6 m of path. The first sign of trouble at 10 m/s² is a 0.58 m excursion (the corridor half-width
is 0.94 m) in one seed: arriving at bend entry faster, with the inner cones not yet visible. The answer
to "is the failure in perception, planning or dynamics?" is **perception first**. The lever for lap time
is seeing farther (longer memory, better ranging at 5–6 m), not more lateral acceleration. Full credit
requires this diagnosis, supported by logging which term of (9.3) binds.

### 9.8 [C] Occlusion

**Expected result and teaching note.** For cones on one side of a straight at lateral offset $y$ and
spacing $s$, consecutive cones are separated in bearing by $\approx ys/x^2$ at range $x$, and a cone
subtends $\approx d/x$ (base diameter $d = 0.036$ m). One hides the next when $ys/x^2 < d/x$, i.e.
$x > ys/d$, which is **20 m** for $y = 1.1$, $s = 0.65$. Mutual occlusion between cones is therefore
negligible within the detector's 6.5 m range on straights, and appears only in bends (an inner cone
hiding an outer one across the track) and behind obstacles. A correct implementation shows almost no
change on straights and a small increase in misses in bends. Students who find a large effect usually
used the cone's *height* instead of its width, or ignored range. Rubric: implementation (4), measured
effect (3), the geometric check (3).

### 9.9 [C] Path as observation, or residual RL

Rubric only (a project-scale problem). Required: (a) a fair comparison: same tracks, detector model,
latency and slew limit, and the same evaluation as the classical follower; (b) five seeds with
bootstrap intervals; (c) completion reliability with Clopper–Pearson bounds, not just lap times;
(d) a residual policy whose correction is bounded (e.g. ±20% of the classical command), so it cannot be
worse than the baseline by more than the bound [Johannink19]. The honest expected outcome on this track
is that a residual policy gains a few percent of lap time where the follower is conservative (bend
entries) and is no more reliable; a path-observation policy learns much faster than the 12-cone policy,
because the structure is given.
