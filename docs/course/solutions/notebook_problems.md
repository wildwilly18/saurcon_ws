# Notebook problems — Guidance

Short answers and the key point each notebook problem should surface. Numbers come from the committed
notebook outputs or the lecture's reference results where cited; answers phrased as "expect" or
"about" (N2.2, N4.3, N7.1, N9.1 in particular) are the expected outcome, **not** run for this manual.
Check them against a student's own run rather than marking a mismatch wrong.

## Notebook 01

- **N1.1** The acceleration phase is **linear** in time up to the commanded speed: the drive is
  rate-limited (4.1 m/s² measured), as (1.4) models, not first-order. Look for a constant slope and an
  abrupt corner, not an exponential approach.
- **N1.2** Clip $a_y$ at $\mu g$; at 5 m/s the grip-limited steady curvature is $\mu g/v^2 = 0.4$ m⁻¹,
  i.e. $\delta = \arctan(0.4L) \approx 0.10$ rad. Steps beyond that saturate.
- **N1.3** The grip-plateau quartiles are 7.5–11.4 m/s² (median 9.8). The training range 8.5–10.5
  covers the central part. Defending it requires noting that the extreme quartiles include transients
  of spin-outs, not steady grip.

## Notebook 02

- **N2.1** Doubling resolution doubles the marker's pixel width, so the ambiguity range roughly
  doubles (about 6–8 m instead of 3–4 m), all else equal.
- **N2.2** The discard fraction rises from ≈ 0 below 2 m to most detections beyond ~4 m; plot it with
  Clopper–Pearson bands.
- **N2.3** A mirrored solution with a 20° orientation flip at 3 m moves the vehicle by about
  $3\times0.35 \approx 1$ m, the same order as the 1.6 m jumps described in Lecture 2 §5.

## Notebook 03

- **N3.1** Without gating, each outlier pulls the estimate by $K\boldsymbol\nu$, a jump of metres that
  decays over the next few fixes.
- **N3.2** With `q_xy = 0`, $P$ in position collapses within seconds; from then on $d^2$ of every good
  fix exceeds the gate and the filter dead-reckons forever (the gating trap of Lecture 3 §5).
- **N3.3** At 2 m/s, 0.3 s of uncompensated latency is a 0.6 m lag along the track; compensation with
  (3.7) removes it to the odometry drift over 0.3 s (millimetres).

## Notebook 04

- **N4.1** The verdict flips near the analytic threshold of problem 4.2 scaled to the notebook's
  geometry ($\sigma \approx D/(3N)$ with $D = 3.43$ m and $N$ the links in the loop).
- **N4.2** The total-cost χ² test is *less* sensitive: a closure spread thinly over many links raises
  the total cost only slightly, while the per-link test sees the worst link. Per-link tests catch
  "spread-out" false closures; total-cost tests catch many small inconsistencies.
- **N4.3** Without heading bias, residual error is a random walk; one closure per lap typically
  reaches 5 cm RMS. Report the number with the seed variation.

## Notebook 05

- **N5.1** A 10% higher $\mu g$ raises corner speeds by $\sqrt{1.1}$, about 4.9%, and shortens the
  bound by somewhat less (only the bends are grip-limited).
- **N5.2** The policy runs wide on entry, cuts toward the inside, and exits wide, the classic racing
  line, within the corridor.
- **N5.3** Report completion with an interval; a policy weighted 30% toward the basement oval in
  training often still completes it, but at a lower speed. Any failure is informative.

## Notebook 06

- **N6.1** With `condim="1"` the contact is frictionless: the block does not decelerate (it slides
  until something else stops it).
- **N6.2** At `kv = 20` the actuator torque saturates at ±2 N·m every step, alternating sign; the
  oscillating torque on the light wheel is the hop (Lecture 8 §4).
- **N6.3** At 4 m/s mid-corner the sideslip is a few degrees: small but non-zero, unlike the bicycle
  model's zero at the rear axle.

## Notebook 07

- **N7.1** The rear lets go between about 2 and 4 m/s² of braking at 6.5 m/s and 0.04 rad (the exact
  threshold depends on the calibrated friction).
- **N7.2** Expect non-zero crash rates for the bicycle-trained policies under randomisation; report
  them as $k/20$ with Clopper–Pearson intervals.
- **N7.3** Front brakes remove the brake-induced oversteer (problem 8.4) and gain lap time by
  allowing later, harder braking; after the change, the bicycle model and MuJoCo agree on the outcome.

## Notebook 08

- **N8.1** A 0–32 hue band picks up the warehouse's orange rack beams (hue 7–8); the metric shape
  filter (3–12 cm tall, ≤ 7 cm wide, on the floor) rejects most of them.
- **N8.2** At 0.5 s the bend is nearly blind (problem 9.3: 1.7 cones within 2 m); at 4 s more cones
  persist. With large odometry drift a long horizon would place remembered cones wrongly, which is the
  limit on the horizon on a real car.
- **N8.3** See problem 9.8: little change on straights, a small increase in misses in bends.

## Notebook 09

- **N9.1** The gate path fails more often as misses rise. Expect the fallback share to grow steeply
  beyond about 30–40% misses on the synthetic bend; plot it with seed bands.
- **N9.2** Adding the 50 ms pose prediction mainly helps small lookaheads, whose instability comes
  from phase lag. It does not rescue 0.35 m but reduces the error of the 0.9 m case further.
- **N9.3** See problem 9.7: no failure up to 10 m/s² in the reference runs; the binding limit is
  perception.
- **N9.4** On the failing frame, a shortest path over the midpoint graph finds the same path as the
  greedy chain *after* the fixes; *before* them, it would also have accepted the bad chord, because its
  midpoint is short and cheap to reach. The fix is in the validity tests, not the search.
