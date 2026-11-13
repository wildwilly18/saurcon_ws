# Notation and conventions

These conventions hold in every lecture. Where a symbol is overloaded in the literature, the
choice made here is stated, and lectures say so if they deviate locally.

## Typography

| Object | Convention | Example |
|---|---|---|
| Scalar | italic | $v,\ \delta,\ L$ |
| Vector | bold lower case | $\mathbf x,\ \mathbf z,\ \boldsymbol\nu$ |
| Matrix | upper case | $P,\ Q,\ K,\ H$ |
| Rotation matrix | $\mathbf C$ (to keep $R$ for noise) | ${}^{A}\mathbf C_{B}\in SO(2)$ or $SO(3)$ |
| Estimate, prediction | hat, superscript minus | $\hat{\mathbf x}_k,\ \hat{\mathbf x}_k^-$ |
| Random variable distributed as | $\sim$ | $\mathbf w\sim\mathcal N(\mathbf 0, Q)$ |
| Time index, step | $k$, $\Delta t$ | control step $\Delta t = 50$ ms |

## Frames and transforms (REP-105)

| Frame | Symbol | Meaning |
|---|---|---|
| `world` | $\{W\}$ | Simulator frame (Gazebo ground truth) |
| `map` | $\{M\}$ | Globally consistent, may jump on correction |
| `odom` | $\{O\}$ | Continuous, drifts |
| `base_link` | $\{B\}$ | Rigid with the car, origin at the **rear-axle centre**, $x$ forward, $y$ left |
| camera optical | $\{C\}$ | $x$ right, $y$ down, $z$ along the optical axis |

${}^{A}T_{B}$ is the pose of frame $B$ expressed in frame $A$ (it maps coordinates in $B$ to
coordinates in $A$): ${}^{A}\mathbf p = {}^{A}T_{B}\,{}^{B}\mathbf p$. Composition chains
inner indices, ${}^{A}T_{C} = {}^{A}T_{B}\,{}^{B}T_{C}$. For planar poses
$\mathbf x = (x, y, \psi)$ we write composition as $\mathbf x_1 \oplus \mathbf x_2$ and the
relative pose as $\ominus\mathbf x_1 \oplus \mathbf x_2$. Angles are wrapped to $(-\pi, \pi]$
with $\operatorname{wrap}(\theta)=\operatorname{atan2}(\sin\theta,\cos\theta)$.

## Vehicle

| Symbol | Meaning | SAURCON value |
|---|---|---|
| $L$ | wheelbase | 0.254 m |
| $T_w$ | track width | 0.165 m |
| $\delta$ | front (road-wheel) steering angle, $|\delta|\le\delta_{\max}$ | $\delta_{\max}=0.786$ rad |
| $\psi$, $\dot\psi$ | heading, yaw rate | |
| $v$ | speed of the rear-axle centre | |
| $\kappa = 1/\rho$ | path curvature, turn radius | |
| $a_x$, $a_y$ | longitudinal, lateral acceleration | grip $\mu g\approx 10$ m/s² |
| $\tau_\delta$ | steering time constant | ≈ 0.2 s |

Yaw rate is always $\dot\psi$, never $r$, because $r$ is the reward in reinforcement learning.

## Estimation

| Symbol | Meaning |
|---|---|
| $\mathbf x_k$, $\mathbf u_k$, $\mathbf z_k$ | state, input, measurement |
| $f$, $h$ | process and measurement models |
| $Q$, $R$ | process and measurement noise covariances |
| $P$ | state covariance |
| $\boldsymbol\nu = \mathbf z - h(\hat{\mathbf x}^-)$, $S$ | innovation and its covariance |
| $d^2 = \boldsymbol\nu^\top S^{-1}\boldsymbol\nu$ | squared Mahalanobis distance (normalised innovation squared) |
| $\Omega = \Sigma^{-1}$ | information matrix |

## Reinforcement learning

| Symbol | Meaning |
|---|---|
| $s_t$, $a_t$, $r_t$ | state (or observation $o_t$), action, reward |
| $\pi_\theta(a\mid s)$ | stochastic policy with parameters $\theta$ |
| $\gamma$, $\lambda$ | discount, GAE parameter |
| $V^\pi$, $Q^\pi$, $A^\pi$ | value, action-value, advantage |
| $\rho_t(\theta)$ | probability ratio $\pi_\theta/\pi_{\theta_\text{old}}$ |

## Units

SI throughout: metres, seconds, radians, m/s, m/s². Images are $640\times400$ px unless stated;
pixel coordinates $(u, v)$ have their origin at the top-left corner.
