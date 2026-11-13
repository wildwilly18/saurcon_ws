# Lecture 6 — Solutions

### 6.1 [T] GAE by hand

Notebook 05's example: rewards $r = (0.1, 0.2, -10)$ (a crash at step 3), values
$V = (1.0, 1.1, 0.5, 0)$ with a terminal value of 0, $\gamma = 0.99$, $\lambda = 0.95$, $\gamma\lambda = 0.9405$.

$$
\delta_2 = -10 + 0 - 0.5 = -10.5,\quad
\delta_1 = 0.2 + 0.99\cdot0.5 - 1.1 = -0.405,\quad
\delta_0 = 0.1 + 0.99\cdot1.1 - 1.0 = 0.189.
$$

$$
\hat A_2 = -10.5,\quad \hat A_1 = -0.405 + 0.9405\cdot(-10.5) = -10.28,\quad
\hat A_0 = 0.189 + 0.9405\cdot(-10.28) = -9.48.
$$

This matches the notebook (`[-9.48, -10.28, -10.5]`). With $\lambda = 1$ the sum telescopes:
$\sum_l\gamma^l\delta_{t+l} = \sum_l\gamma^l r_{t+l} - V(s_t)$ (the terminal value is 0), the
Monte-Carlo advantage. Observe the interpretation: all three actions are blamed for the crash, discounted
by $\gamma\lambda$ per step back.

### 6.2 [T] Baselines

See the lecture's answer for unbiasedness. **Variance-minimising constant baseline.** For a scalar
parameter the per-sample estimator is $g(R - b)$ with $g = \nabla\log\pi$. Its variance is
$\mathbb E[g^2(R-b)^2] - (\mathbb E[gR])^2$, since the mean does not depend on $b$. Setting the derivative
in $b$ to zero gives $b^* = \mathbb E[g^2R]/\mathbb E[g^2]$, which equals $\mathbb E[R]$ only if $g^2$
and $R$ are uncorrelated. In practice the state-dependent $V(s)$ is used: not optimal, but close and
learnable.

### 6.3 [T] Potential-based shaping

See the lecture's answer. For full credit, handle termination: define $\Phi(\text{terminal}) = 0$ (or
any constant shared by all terminal states). Otherwise policies that terminate in different states
receive different constant offsets and the ordering *can* change. Progress-as-potential is safe on a
loop because the lap counter, not arc length modulo the lap, is the potential.

### 6.4 [C] No smoothness penalty

**Expected result.** Steering activity roughly doubles and lap time changes little. The closest
reference in the course is the cone task (Lecture 9 §5): mean steering change 8.2° per step without the
smooth-driving terms against 4.2° with them, and offset standard deviation on straights 0.161 m against
0.093 m. Require three seeds per condition and a paired comparison (Lecture 7 §5). Strong answers
predict the consequence on the real car: the servo's slew limit makes high-activity steering lag, and
the lag becomes a weave.

### 6.5 [C] No domain randomisation

**Expected result.** The non-randomised policy is *faster* in the bicycle model it was trained in and
*less reliable* in MuJoCo, where the dynamics differ: more spins under braking (Lecture 8 §6) and
completion rates with wide intervals over five seeds. Grade the experimental design: five training
seeds per condition, evaluation over ≥ 10 episodes per seed, bootstrap intervals, and a clear
statement that "faster in training, worse in transfer" is the expected pattern [Tobin17; Peng18].

### 6.6 [T] "−1 per step until the lap is complete"

Two failures compound. First, **sparse signal**: early policies never complete a lap, so every episode
has the same return (−1 per step until the time limit), all advantages are ≈ 0, and the gradient
carries no information. Second, and decisively, **termination becomes attractive**: a crash ends the
episode, which *stops the −1s*. An episode that crashes after 20 steps returns about −20 (minus the crash
penalty); one that drives carefully for 900 steps returns −900. Unless the crash penalty exceeds the
remaining time's cost, the optimal policy is to crash immediately. This is the mirror image of the
"parking" degeneracy in §4: the reward must make degenerate behaviour exactly as bad as the failure you
fear. Rubric: zero-advantage argument (4), crash incentive with a numerical example (4), fix (2).

### 6.7 [T] Acceptance test for a learned policy

**Model answer** (any defensible numbers accepted if justified):

1. **Conditions:** the Gazebo full stack with RTAB-Map running, on the racetrack (both directions), the
   basement oval and the feature warehouse; the same `cone_follower_node` safety checks wrapped around
   the policy; the same latency, servo slew and observation as in training.
2. **Reliability bar:** at least 29 consecutive clean 3-lap runs per track, giving a 95% lower bound ≈ 0.9
   (Lecture 7, Figure 7.1); the classical follower must be measured the same way, and the policy's lower
   bound must not be below the follower's point estimate.
3. **Performance margin:** paired lap-time difference with a 95% interval excluding zero in the policy's
   favour (≈ 14 paired runs per track for a 0.3 s margin; problem 7.4).
4. **Seeds:** the claim must hold for at least 3 of 5 independently trained seeds, so it is not one lucky
   network.
5. **Disqualifiers (any single occurrence):** leaving the cone corridor; a command issued on stale inputs
   (fake-clock tests); a frame or origin mismatch found in review; a failure that the classical follower
   handles in the same situation.

Rubric: equal conditions (2), statistical bar with numbers (3), margin test (2), seeds (1), disqualifiers (2).
