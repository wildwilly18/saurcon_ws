# Chapter 3 — State Estimation with the Unscented Kalman Filter

**Notebook:** [03_unscented_kalman_filter.ipynb](notebooks/03_unscented_kalman_filter.ipynb)

## Learning objectives

- Derive the Kalman filter prediction and update, and explain what the covariance means.
- Explain why nonlinear models need an EKF or UKF, and implement the unscented transform.
- Choose process and measurement noise, gate outliers with the Mahalanobis distance, and check filter consistency.
- Handle sensor bias, measurement latency and numerical failure in a deployed filter.

## 1. The estimation problem

SAURCON's filter estimates $\mathbf x = [x,\ y,\ \psi,\ v]^\top$. Wheel speed and the
gyro's yaw rate drive a **prediction**; pose fixes (ArUco markers, or RTAB-Map)
arrive occasionally as **measurements** $\mathbf z = [x,\ y,\ \psi]^\top$. Each
quantity is a Gaussian belief: mean $\hat{\mathbf x}$ and covariance $P$.

## 2. The Kalman filter in one page

Predict with model $\mathbf x_{k} = f(\mathbf x_{k-1}, \mathbf u_k) + \mathbf w$,
$\mathbf w \sim \mathcal N(0, Q)$:

$$\hat{\mathbf x}^- = f(\hat{\mathbf x}, \mathbf u), \qquad P^- = F P F^\top + Q.$$

Update with $\mathbf z = h(\mathbf x) + \mathbf n$, $\mathbf n \sim \mathcal N(0, R)$:

$$\boldsymbol\nu = \mathbf z - h(\hat{\mathbf x}^-), \quad S = H P^- H^\top + R, \quad K = P^- H^\top S^{-1},$$
$$\hat{\mathbf x} = \hat{\mathbf x}^- + K\boldsymbol\nu, \qquad P = (I - KH)P^-(I-KH)^\top + K R K^\top.$$

The last line is the **Joseph form**: algebraically equal to $(I-KH)P^-$ but it keeps
$P$ symmetric positive-definite under rounding.

## 3. The unscented transform

The motion model is nonlinear (heading inside sines and cosines). Rather than
linearising (EKF), the UKF pushes $2n+1$ **sigma points** through the true model:

$$\mathcal X_0 = \hat{\mathbf x}, \qquad \mathcal X_{\pm i} = \hat{\mathbf x} \pm \left(\sqrt{(n+\lambda)P}\right)_i,
\qquad \lambda = \alpha^2(n+\kappa) - n,$$

with weights $W_0^m = \lambda/(n+\lambda)$,
$W_0^c = W_0^m + (1-\alpha^2+\beta)$, $W_i = 1/(2(n+\lambda))$. The predicted mean
and covariance are the weighted mean and scatter of the transformed points. The
matrix square root is a Cholesky factor. Angles need care: average and difference
headings with `atan2(sin, cos)`.

SAURCON uses $n=4$, $\alpha = 0.1$, $\beta = 2$, $\kappa = 0$, which makes
$W_0^c \approx -96$. Negative weights are legal but can make the predicted
covariance indefinite, so the code symmetrises $P$, floors its diagonal, and adds
jitter if Cholesky fails (`sigmaRoot`, `conditionCovariance`).

## 4. The SAURCON motion model

With gyro yaw rate $\omega$ (bias-corrected) and wheel speed $v$ as inputs, over
$\Delta t$ (the constant-turn-rate model):

$$x' = x + \frac{v}{\omega}\big(\sin(\psi+\omega\Delta t) - \sin\psi\big), \quad
y' = y + \frac{v}{\omega}\big(\cos\psi - \cos(\psi+\omega\Delta t)\big), \quad \psi' = \psi + \omega\Delta t,$$

falling back to straight-line motion when $|\omega| \approx 0$. Process noise covers
gyro noise (heading), speed noise, and a position term that grows with speed to
represent wheel slip.

## 5. Making a filter that survives contact with reality

**Outlier gating.** Before using a measurement, compute
$d^2 = \boldsymbol\nu^\top S^{-1}\boldsymbol\nu$. For a correct 3-D measurement it
is $\chi^2_3$-distributed; reject if $d^2$ exceeds a threshold (SAURCON uses 5σ,
$d^2 > 25$). **Trap:** if $P$ becomes too small, every true measurement is rejected
forever. The original filter gave position no process noise, so after a few
seconds it ignored all fixes; the fix adds process noise and re-initialises after 15
consecutive rejections.

**Bias.** Case study below.

**Consistency.** A filter is *consistent* if its errors match its covariance:
about 99.7% of errors inside ±3σ. Over-confident filters gate out good data;
under-confident ones are sluggish. Notebook 03 plots this; chapter 4 shows the
odometry filter is ~7× under-confident in position on purpose.

**Latency.** A pose fix describes the moment its camera image was taken, often
100–500 ms ago. At 8 m/s that is up to 4 m. SAURCON's global filter shifts each
fix to the present using the odometry travelled since its timestamp:
$z_\text{now} = z_{t} \oplus \left(T^{\text{odom}}_{t}\right)^{-1} T^{\text{odom}}_\text{now}$.

## 6. Case study — the 1-second bias calibration

At start-up the filter averaged **100** stationary gyro samples (1 s at 100 Hz) to
estimate bias. The simulated gyro has *no* bias, only noise with
$\sigma_n = 0.009$ rad/s, so the "bias estimate" was pure noise with standard
deviation $0.009/\sqrt{100} = 0.0009$ rad/s. Subtracting it injected that error:
over a 216 s run, **13° of heading drift** and 1.7 m RMS position error. Earlier
runs had looked fine by luck of the draw.

The fix uses physics: an Ackermann car **cannot yaw while its wheels are stopped**,
so every gyro sample taken while stationary is another bias sample. The filter keeps
a running mean (capped at 6000 samples so slow bias drift is tracked) and rejects
samples above 0.1 rad/s (knocks). Odometry error fell from 1.73 m to 0.08–0.18 m
RMS over four laps.

## 7. Case study — initialization order in C++

When a second filter instance was added, both instances behaved as the global one.
The node class declared `bool fuse_{true};` *after* the filter object whose
constructor set it. C++ initialises members in declaration order, so the default
initialiser ran last and overwrote the parameter. The bug only surfaced as a TF
symptom ("frame odom does not exist") in another node. Rule: never set a member
from another member's initialiser unless the order is guaranteed.

## How SAURCON does it

| Concept | Where |
|---|---|
| UKF core (sigma points, predict, update, gating, bias) | `src/saurcon_nav/src/state_estimator.cpp` |
| ROS wrapper, modes, latency compensation, TF | `src/saurcon_nav/src/state_estimator_node.cpp` |
| Unit tests (dead reckoning, bias refinement) | `src/saurcon_nav/test/test_dead_reckoning.cpp` |
| UKF plots against ground truth | `scripts/sim_eval/plot_ukf.py` |

## Exercises

1. ★ Show that the Joseph form equals $(I-KH)P^-$ when $K$ is the optimal gain.
2. ★ In the notebook, vary $\alpha$ and observe $W_0^c$. When does the predicted covariance become indefinite?
3. ★★ Add a gyro-bias state to the notebook filter; show it converges using pose fixes alone.
4. ★★ Compute the NEES (normalised estimation error squared) for the notebook run. Is the filter consistent?
5. ★★★ Derive the error introduced by applying a 300 ms-old pose fix without latency compensation at 6 m/s on a 2 m radius bend.
