# Lecture 3 — Solutions

### 3.1 [T] Joseph form

See the lecture's answer. For the second part: for an arbitrary gain $K$ the Joseph form equals
$P^- - KHP^- - P^-H^\top K^\top + KSK^\top$, which is the true error covariance of the estimator
$\hat{\mathbf x}^- + K\boldsymbol\nu$, while $(I-KH)P^-$ equals it only when $KS = P^-H^\top$, i.e. at
the optimal gain. So with a suboptimal gain (for example after gating heuristics, or with a gain
computed in single precision), $(I-KH)P^-$ is simply the wrong covariance, and it can be indefinite.

### 3.2 [C] Sweeping α

**Reference result** (reference script; CTRV prediction over 0.5 s at 3 m/s and 2 rad/s, position
σ 5 cm, speed σ 0.5 m/s, no process noise added):

| α | $W^c_0$ | min eigenvalue of predicted $P$, σ_ψ = 0.3 rad | σ_ψ = 1.5 rad |
|---|---|---|---|
| 0.001 | −1.0×10⁶ | 8.1×10⁻⁴ | 8.1×10⁻⁴ |
| 0.01 | −1.0×10⁴ | 8.1×10⁻⁴ | 8.2×10⁻⁴ |
| 0.1 | −96 | 8.1×10⁻⁴ | 8.3×10⁻⁴ |
| 0.5 | −0.25 | 8.3×10⁻⁴ | 1.3×10⁻³ |
| 1.0 | 2 | 8.8×10⁻⁴ | 2.5×10⁻³ |

**Teaching note.** The predicted covariance stayed **positive definite for every α**, even with a
1.5 rad heading uncertainty. Students who expect a sign change will not find one, and should explain
why. Write $P_y = \sum_{i\ge1}W_i\,\Delta_i\Delta_i^\top + W^c_0\,\Delta_0\Delta_0^\top$ with
$\Delta_i = g(\mathcal X_i) - \hat{\mathbf y}$ and $\mathbf d = \Delta_0 = g(\hat{\mathbf x}) - \hat{\mathbf
y}$. As α → 0 the weighted mean converges to $g(\hat{\mathbf x}) + \tfrac12\operatorname{tr}(\nabla^2 g\,P)$,
so $\mathbf d$ tends to a fixed second-order offset; it does **not** vanish. Expanding
$\Delta_{\pm i} = \mathbf d \pm \alpha\sqrt n\,J\mathbf s_i + O(\alpha^2)$, the outer points contribute
$(\sum_{i\ge1}W_i)\,\mathbf d\mathbf d^\top = \frac{n}{n+\lambda}\mathbf d\mathbf d^\top \approx \alpha^{-2}\mathbf d\mathbf
d^\top$, and the centre point contributes $W^c_0\,\mathbf d\mathbf d^\top \approx (2 + \beta - \alpha^{-2})\,\mathbf
d\mathbf d^\top$. The $\alpha^{-2}$ terms **cancel exactly**, leaving
$P_y \approx JPJ^\top + (\beta + \dots)\,\mathbf d\mathbf d^\top + O(\alpha^2)$, which is positive
semi-definite whenever $\beta\ge0$. Indefiniteness therefore needs higher-order effects (strong
curvature at moderate α, or a non-Gaussian $P$), which smooth vehicle models rarely produce.

The practical hazard is the cancellation itself, which is **numerical**: with α = 0.001 the
covariance is computed from terms of magnitude $10^6\,\|\mathbf d\|^2$ that cancel to the
$10^{-3}$-scale answer, losing about nine of float64's sixteen significant digits; in float32 the
result is noise. That, plus measurement updates with inconsistent gains (3.1), is why the
C++ filter symmetrises, floors and jitters $P$. Full marks: the sweep, the observation, and this
explanation.

### 3.3 [C] Gyro-bias state

Augment $\mathbf x = (x, y, \psi, v, b)$ with $\dot b = w_b$ (a random walk) and use $\omega - b$ in
(3.6). **Observability.** Pose fixes measure $\psi$ directly, and between fixes heading drifts by
$b\,\Delta t$, so $b$ is observable from **two heading measurements separated in time, even while
stationary**. With position-only fixes, $\psi$ is observed only through the direction of motion, so
$b$ becomes observable only while $v \ne 0$. Expected result: from a 0.002 rad/s true bias, the
estimate converges to within $10^{-4}$ rad/s in tens of seconds with 2 Hz heading fixes; its
covariance shrinks as $1/T$ while stationary and faster while turning. Rubric: model (3), working
convergence plot with 3σ band (3), observability argument (4).

### 3.4 [C] Consistency over 50 seeds

**Method.** Run the notebook's simulation with 50 seeds. At each time step average the NEES
$\tilde{\mathbf x}^\top P^{-1}\tilde{\mathbf x}$ over seeds, and plot it against the 95% band of
$\chi^2_{4\cdot50}/50$, which is **[3.25, 4.82]**. Do the same for the NIS of accepted fixes against
$\chi^2_{3\cdot50}/50$, **[2.36, 3.72]**.

**Expected result.** The time-averaged NEES lies **below** the band in position: the filter is
*under-confident*. Notebook 03 already hints at it: 100% of $x$ errors fall inside 3σ, where a
consistent filter would place about 99.7% there and its typical errors would be near 1σ. The cause is
deliberate: position process noise is inflated so that the gate never locks out fixes (§5). Strong
answers report which state is inconsistent and in which direction, and connect under-confidence to
its cost (slower convergence after a fix) rather than calling it a bug.

### 3.5 [T] An uncompensated 300 ms fix

See the lecture's answer: 1.74 m and 0.9 rad (52°). A grader should also accept a gate-based
discussion: with $S$ dominated by $R$ (say 5 cm and 0.5°), $d^2$ is in the thousands, so the fix is
rejected every time and the filter loses all corrections in bends, which is worse than an occasional
bad update.

### 3.6 [T] Information form

With $Y = P^{-1}$ and $\mathbf y = Y\hat{\mathbf x}$, the measurement update is additive:

$$Y = Y^- + H^\top R^{-1}H,\qquad \mathbf y = \mathbf y^- + H^\top R^{-1}\mathbf z,$$

which is cheap, and sparse if $H$ touches few states (many independent measurements just add). The
prediction is expensive: $Y^- = (FY^{-1}F^\top + Q)^{-1}$ needs an inversion (or the Woodbury identity),
and marginalising out the old state couples everything it touched, filling $Y$ in. This is the
filtering-versus-smoothing argument of SLAM (Lecture 4 §1): a *smoother* keeps all past poses as
variables, so its information matrix (4.2) stays sparse, with one block per measurement, and never
pays the marginalisation fill-in. Rubric: update derivation (4), prediction derivation and cost (3),
connection to SLAM sparsity (3).
