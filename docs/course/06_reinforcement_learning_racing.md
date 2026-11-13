# Chapter 6 — Reinforcement Learning for Racing

**Notebook:** [05_rl_racing.ipynb](notebooks/05_rl_racing.ipynb)

## Learning objectives

- Formulate racing as a Markov decision process: state, action, reward, termination.
- Derive the policy-gradient theorem, advantage estimation (GAE) and PPO's clipped objective.
- Design rewards that optimise lap time without exploitable shortcuts.
- Use a fast surrogate simulator with domain randomization, and validate transfer.

## 1. The MDP

| Element | SAURCON choice |
|---|---|
| State / observation (31) | speed, yaw rate, steering, previous action, lateral offset and heading error from the centreline, and 12 centreline points 0.5–15 m ahead in the car frame |
| Action (2) | speed command 0–12 m/s, steering angle ±0.786 rad (both scaled to [−1, 1]) |
| Step | 50 ms (20 Hz) |
| Reward | metres of progress along the centreline this step, minus $0.02\lVert a_t - a_{t-1}\rVert^2$ |
| Termination | leaving the cone corridor or exceeding the grip limit (−10) |
| Episode | random track (racetrack or basement, either direction), random start, 45 s |

**Why these choices.**

- *Body-frame lookahead points* rather than absolute position: the policy learns
  "a left bend 4 m ahead" and transfers to tracks it has not seen.
- *Progress reward*: with discount $\gamma$, maximising discounted progress per step
  means going fast. A lap bonus alone would be too sparse to learn from.
- *Smoothness penalty*: small, so that it stops actuator chatter without making the
  policy timid.
- *Termination as the crash penalty*: ending the episode removes all future reward,
  which is a large implicit penalty. Avoid rewards that pay for *not* finishing.

**Reward hacking to watch for:** progress measured as arc length could be gamed by
cutting across the inside of a corner if the corridor allowed it; projecting onto
the centreline with a search window around the last index prevents jumping to a
different part of the track.

## 2. Policy gradients

For a stochastic policy $\pi_\theta(a\mid s)$ the expected return $J(\theta)$ has
gradient

$$\nabla_\theta J = \mathbb E\!\left[\sum_t \nabla_\theta \log \pi_\theta(a_t\mid s_t)\, A_t\right],$$

where the **advantage** $A_t$ says how much better action $a_t$ was than the
policy's average. With a learned value function $V_\phi$, the TD residual is
$\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$ and **Generalised Advantage
Estimation** blends horizons:

$$A_t^{\text{GAE}} = \sum_{l\ge0} (\gamma\lambda)^l\, \delta_{t+l}.$$

$\lambda=0$ is low-variance but biased; $\lambda=1$ is the unbiased Monte-Carlo
return. SAURCON uses $\gamma = 0.99$ (an effective horizon of
$1/(1-\gamma) = 100$ steps = 5 s, enough to plan braking) and $\lambda = 0.95$.

## 3. PPO

Large policy updates are unstable. PPO maximises a clipped surrogate with
probability ratio $\rho_t = \pi_\theta(a_t\mid s_t)/\pi_{\theta_\text{old}}(a_t\mid s_t)$:

$$L^{\text{CLIP}} = \mathbb E\!\left[\min\!\big(\rho_t A_t,\ \operatorname{clip}(\rho_t, 1-\epsilon, 1+\epsilon)\, A_t\big)\right],$$

so there is no incentive to move $\rho$ outside $[1-\epsilon, 1+\epsilon]$
($\epsilon=0.2$). Each iteration: 12 parallel environments collect 1024 steps
each; 10 epochs of minibatch (4096) gradient steps on the policy and value losses;
repeat. Actions are sampled from a Gaussian during training and the mean is used
at evaluation.

## 4. Sim-to-real (here, sim-to-sim)

Gazebo runs at about real time while rendering the camera, so 20 M training steps
(~280 h of driving) are impossible there. Instead:

1. **Identify** the Gazebo car (chapter 1) and build a fast bicycle model that runs
   ~5,800 steps/s per core.
2. **Randomise** what you are unsure of: grip 8.5–10.5 m/s², acceleration 3.5–4.5,
   braking 4–5, steering lag 0.1–0.3 s, pose noise up to 5 cm, sensing delay up to
   60 ms. The policy cannot overfit one car.
3. **Validate** in the full loop: Gazebo physics, simulated camera, RTAB-Map
   localization on a saved map, the fused UKF, and the state machine. The early
   policy lapped at 16.3 s in Gazebo vs. 16.25 s in training.

The same structure applies to the real car: identify it, retrain or fine-tune with
its parameters, and validate before racing.

## 5. Results

Training curve (single seed, 20 M steps, ~1 h on 12 cores): the flying lap fell
from 22.5 s at 0.25 M steps to **7.35 s** (best, at 18.5 M), with top speed rising
from 2.4 to 9.9 m/s and no crash in any of the 80 evaluation laps. The
standing-start lap is 8.35 s. For comparison, a scripted pure-pursuit driver at
1 m/s laps in 47.7 s.

Notebook 05 computes a physics bound for driving the *centreline* (grip-limited
corners, full acceleration and braking): **7.80 s**. The policy beats it. It is
slower than the bound in the bends (2.9 vs 4.4 m/s; it was trained against grip as
low as 8.5 m/s² and up to 0.3 s steering lag) but uses the ±0.44 m corridor to take
wider lines into and out of them, accelerating earlier and braking later.

*Track note.* These results are for the original racetrack, whose 1.2 m gates gave a
±0.44 m corridor for the car's centre. The racetrack now has 2.2 m gates (chapter 9,
section 8), so `track.py` derives a ±0.94 m corridor there (the basement oval is
unchanged at ±0.44 m). The map-based policies have not been retrained on it; a wider
corridor allows wider lines, so expect faster laps, and compare against the
centreline bound, which does not depend on the width. Notebook 05's committed outputs
are from the old layout.

Those are fast-model numbers for the first policy. Its full-speed Gazebo race
failed (section 6); results after the fix are in `src/saurcon_rl/README.md`.

## 6. Case study — the first full-speed race in Gazebo

A policy trained to 3 m/s transferred almost perfectly (16.3 s in Gazebo vs 16.25 s
in training). The 7.35 s policy did not: on its first lap it reached the far bend
at ~9 m/s, braked, and spun. Comparing the estimated and true pose through the
crash showed two model errors, neither visible at low speed:

1. **Wheel spin corrupted odometry.** Gazebo's drive plugin ramped the rear wheels
   at 5 m/s², above the ~4.1 m/s² the tyres can transmit. The driven wheels spun,
   wheel odometry over-read speed by up to 1 m/s, and between 2 Hz RTAB-Map fixes the
   position estimate ran up to 1 m ahead of the car.
2. **Braking and cornering share grip.** The training model only limited lateral
   acceleration. Gazebo's car brakes with the rear wheels only; braking hard into
   the bend unloaded them and the rear let go.

The fix was physical, not a reward hack: ramp limits just under tyre grip (as a
real speed controller with traction control would), and a friction circle in the
training model, $\sqrt{(k\,a_\text{long})^2 + a_y^2} \le \mu g$ with braking
weighted $k = 1.5$. **The corrected model reproduced the failure** — the old
policy spun 8.9 m into its first braking zone, as in Gazebo — which is the evidence
that it captures what went wrong. The policy was then fine-tuned from its previous
weights.

A second lesson: the crash also stalled Gazebo's physics (real-time factor fell to
1%), so the state machine's 0.25 s command timeout fired continuously. The first
diagnosis — "the machine was busy running notebooks" — was wrong, and was only
caught by re-running on an idle machine and profiling the real-time factor over
the run. Measure before explaining.

## 7. Where the policy's pose comes from

The policy's observation is built from a **global** pose: the track is stored in the
Gazebo world frame, and `/saurcon/nav_state` is converted into it with the world
pose of the frame it is published in (`map_origin`). Two localization modes publish
in different frames, both named `map`:

| Mode | `/saurcon/nav_state` frame | `map_origin` |
|---|---|---|
| ArUco (`use_aruco:=true`) | world (marker map) coordinates | `0 0 0` |
| RTAB-Map, fused (`slam:=true fuse_slam:=true`) | RTAB-Map's map, starting where mapping started | `policy_map_origin`, default `-1.127 0 0` (racetrack spawn) |
| `fuse_slam:=false`, visual odometry, or neither | odometry, which drifts | rejected at launch |

A review found the launch file used the RTAB-Map origin in every mode, so under the
default ArUco localization every position was shifted 1.127 m and every bend came
early. A frame name does not tell you its origin; the launch file now chooses the
origin from the mode and refuses combinations that would feed odometry to a policy
that needs a map pose (`policy_map_origin()` in `full_sim_saurcon.launch.py`, tested
in `src/saurcon_rc/test/test_policy_launch.py`). The node also stops if the state
stops updating (chapter 5).

## 8. Where this went next

- **Driving without a map** (chapter 9): the same PPO setup trained on detected cones
  instead of a stored centreline, including fine-tuning **in Gazebo** itself (the
  answer to exercise 5 is in chapter 9, section 9) and a reward for smooth steering
  (section 10).
- **A classical baseline** (chapter 9, section 12): on the cone task a hand-written
  follower beat every learned policy. Always build the baseline first; it tells you
  what the learning has to beat and what it is for.

## How SAURCON does it

| Concept | Where |
|---|---|
| Track geometry from the cones | `src/saurcon_rl/saurcon_rl/track.py` |
| Environment, observation, reward | `src/saurcon_rl/saurcon_rl/env.py` |
| PPO training, lap evaluation | `src/saurcon_rl/saurcon_rl/train.py` |
| Policy on the car | `src/saurcon_rl/saurcon_rl/policy_node.py` |
| Pose source and origin per launch mode | `src/saurcon_rc/launch/full_sim_saurcon.launch.py` (`policy_map_origin`) |
| Full-loop race harness | `scripts/sim_eval/race_driver.py` |

## Exercises

1. ★ Compute GAE by hand for a 3-step episode (the notebook checks your answer).
2. ★ Train with the smoothness penalty set to 0. What happens to steering in Gazebo?
3. ★★ Remove domain randomization and retrain. Compare fast-env and Gazebo lap times.
4. ★★ Change the reward to "−1 per step until the lap is complete". Why does learning stall?
5. ★★★ Fine-tune the policy in the Gazebo full loop. Design the reset procedure without breaking the odometry filter (hint: what does teleporting the car do to `odom`?). Compare your design with `gazebo_cone_env.py` (chapter 9, section 9).
6. ★ Launch with `policy_model:=... use_aruco:=true` and with `slam:=true fuse_slam:=false`. What does each do, and why?
