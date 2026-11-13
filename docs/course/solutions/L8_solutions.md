# Lecture 8 — Solutions

### 8.1 [C] Floor friction 0.5

MuJoCo combines the friction of two contacting geoms by taking the **maximum** of each coefficient
(unless contact priorities or explicit pair friction are set). Lowering the floor's friction to 0.5
therefore changes nothing if the block's coefficient is higher: the block still decelerates at
$\mu_\text{block}\,g$. Only a block with a coefficient below 0.5 would slide at $0.5\,g$. Students who
report "no change" and then explain the maximum rule get full marks; a common error is to expect the
average or the product (ODE and some other engines use different rules, Lecture 8 §5).

### 8.2 [C] Time step 0.5 ms

**Expected result.** The straight-line run is the same to within ~1% in speed and position (the 2 ms
step is already converged for rolling contact with `implicitfast`), contact penetration is somewhat
smaller, and wall-clock cost rises about 4× (four times as many physics steps per control step).
Strong answers check *convergence*: halve the step again and show that the difference shrinks.

### 8.3 [T] Effective stiffness from `solref`

See the lecture's answer. Derivation: (8.2) with time constant $\tau_c$ and damping ratio $\zeta$ sets
the reference acceleration of a unit-mass spring–damper with $b = 2/\tau_c$ and $k = 1/(\tau_c\zeta)^2$
(MuJoCo's convention; the impedance from `solimp` scales the result). At rest, $k\,r = g$ gives
penetration $r = g\,\tau_c^2\zeta^2$, ≈ 3.9 mm for the defaults, independent of mass because the
constraint is formulated per unit effective mass.

### 8.4 [C] Front-wheel braking

**Method.** Add velocity actuators on the front wheel joints, enabled only while the commanded speed is
below the current speed, with a target of the commanded speed. Replay notebook 07 §2 (6.5 m/s, 0.04 rad,
braking at 4 m/s²).

**Expected result.** With rear-only braking the yaw rate reaches nearly double $v\tan\delta/L$
(brake-induced oversteer). With front braking it stays close to the kinematic value, and with front-only
braking it falls *below* (understeer). The general point: brake balance moves the understeer gradient
(problem 1.2). Rubric: implementation (4), the three cases (4), connection to $K_{us}$ (2).

### 8.5 [C] MJX port

Rubric only (results depend on hardware). Required: the step function written with `jax.numpy` and no
per-step Python control flow (`jax.lax.cond` for branches, `vmap` over environments), the reward and
termination ported faithfully (test against the CPU environment on identical inputs to 1e-5), and a
throughput plot against the number of parallel environments. Typical outcome: thousands of
environments per GPU and one to two orders of magnitude more steps per second than 12 CPU cores, with
contact-rich models gaining less. Penalise speed claims without a correctness check.

### 8.6 [T] Yaw stability by linearisation

**Method.** Find a steady turn (constant $v$, $\delta$) by simulating to steady state. Compute the
discrete transition Jacobian $A = \partial\mathbf x_{k+1}/\partial\mathbf x_k$ with `mjd_transitionFD`.
Restrict to the lateral–yaw subspace (lateral velocity and yaw rate, removing the neutrally stable
position and heading directions) and report the eigenvalues; stability needs $|\lambda| < 1$. Repeat
with a braking torque applied.

**Expected result.** Coasting: the lateral–yaw eigenvalues lie well inside the unit circle. Braking:
they move toward and, at sufficient deceleration, past the unit circle; the turn becomes unstable,
which is a spin. This is the linear counterpart of $K_{us}$ turning negative (1.7): the critical speed
$\sqrt{-L/K_{us}}$ falls below the current speed. Rubric: equilibrium found (2), correct Jacobian and
subspace (4), braking comparison (2), link to $K_{us}$ (2).
