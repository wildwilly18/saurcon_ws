# Lecture 1 — Solutions

### 1.1 [T] Ackermann angles at ρ = 2 m

$\tan\delta_\text{in} = 0.254/(2 - 0.0825) = 0.13246$ ⇒ $\delta_\text{in} = 0.1317$ rad = **7.55°**;
$\tan\delta_\text{out} = 0.254/(2 + 0.0825) = 0.12197$ ⇒ $\delta_\text{out} = 0.1214$ rad = **6.95°**.
The centreline (bicycle) angle is 7.24°. Notebook 01, cell 3, prints the same values (and 15.47°/13.21°
at 1 m, where the difference between the two wheels is 2.3°).

### 1.2 [T] Steady-state steering (1.7)

At steady state $\dot v_y = \ddot\psi = 0$. The moment equation gives $l_f F_{yf} = l_r F_{yr}$; with
$F_{yf} + F_{yr} = m v_x\dot\psi = m a_y$,

$$
F_{yf} = \frac{l_r}{L}m a_y,\qquad F_{yr} = \frac{l_f}{L}m a_y,\qquad
\alpha_f = \frac{l_r m a_y}{L C_f},\qquad \alpha_r = \frac{l_f m a_y}{L C_r}.
$$

From (1.5), $\alpha_f - \alpha_r = \delta - \frac{(v_y + l_f\dot\psi) - (v_y - l_r\dot\psi)}{v_x}
= \delta - \frac{L\dot\psi}{v_x} = \delta - \frac{L}{\rho}$. Hence

$$\delta = \frac{L}{\rho} + \alpha_f - \alpha_r = \frac{L}{\rho} + \frac{m}{L}\Big(\frac{l_r}{C_f} - \frac{l_f}{C_r}\Big)a_y.$$

**Rear-only braking** moves $K_{us}$ toward **negative (oversteer)**: braking transfers load to the
front axle, raising $C_f$ and lowering $C_r$, and the rear tyres spend part of their friction ellipse
on braking, lowering their available lateral force further. Both reduce $K_{us}$. This is exactly the
brake-induced oversteer MuJoCo predicted (Lecture 8 §6).

**Rubric.** Steady-state equations (3); slip-angle difference (3); final form (2); braking sign with a
mechanism (2).

### 1.3 [T] 10% error in the kinematic gain

See the lecture's answer: $v = v_\text{ch}/\sqrt{10}\approx 0.32\,v_\text{ch}$. Strong answers note
that this requires $K_{us} > 0$; for an oversteering car the kinematic model *under*-predicts yaw gain,
and the relevant speed is a fraction of the critical speed instead.

### 1.4 [C] Speed profile with the friction ellipse

**Method.** In Algorithm 1.1, replace the fixed bounds by the ellipse: at each sample, with
$a_y = v^2\kappa$, the forward pass may accelerate by $\min(a, \sqrt{(\mu g)^2 - a_y^2})$ and the
backward pass may brake by $\min(b, \sqrt{(\mu g)^2 - a_y^2}/k)$.

**Reference result** (`reference_results.py`, racetrack centreline, $\mu g = 10$, $a = 3.8$,
$b = 4.0$ m/s²):

| Model | Lap-time bound |
|---|---|
| separate bounds (Algorithm 1.1) | 7.798 s |
| circle, $k = 1$ | 7.806 s |
| ellipse, $k = 1.5$ | 7.808 s |

The largest speed difference between $k = 1$ and $k = 1.5$ is **0.009 m/s**, at bend entry
($s = 41.3$ m).

**Teaching note.** Students expect a visible effect and find almost none. The reason is the track's
geometry: the stadium's curvature jumps from zero to $1/2$ m⁻¹ at the bend entry (only smoothed over
about 25 cm), so all braking happens on the straight, where $a_y \approx 0$ and the ellipse imposes
nothing. The braking weight matters only where braking and cornering *overlap*: trail-braking into
bends with gradually increasing curvature, or a racing line that turns in while still braking. That
is exactly where the Gazebo car spun (Lecture 6 §6): the policy braked *in* the bend, which no
centreline profile does. Award full marks for an answer that finds the small effect *and* explains it.

### 1.5 [C] Steering time constant

**Method.** Discretise $\delta_{k+1} = \phi\,\delta_k + (1-\phi)\,\delta_{\text{cmd},k}$ and regress
$\delta_{k+1} - \delta_{\text{cmd},k}$ on $\delta_k - \delta_{\text{cmd},k}$ (a one-parameter, no-intercept
regression), giving $\hat\phi$, its standard error $\hat\sigma/\sqrt{\sum x_k^2}$, and
$\hat\tau_\delta = -\Delta t/\ln\hat\phi$ with standard error $\Delta t\,\operatorname{se}(\hat\phi)/(\hat\phi\ln^2\hat\phi)$
by the delta method. Steering is not measured directly in the log, so in practice students fit the
**yaw-rate** response, which adds the vehicle's own lag.

**Reference.** Notebook 01, cell 13, fits the yaw-rate step at 3 m/s: steady yaw rate 3.24 rad/s
against 3.65 kinematic, and **τ ≈ 0.32 s**. This is larger than the 0.2 s used in training, for the
reason the notebook states: the step demands $a_y \approx 10.8$ m/s², at the grip limit, so the
response contains tyre saturation as well as servo lag. Accept 0.2–0.35 s with a correct explanation.
Raw finite differences give a *smaller* τ than smoothed data (attenuation bias, problem 1.6, pulls
$\hat\phi$ toward 0).

**Rubric.** Correct regression (4); uncertainty (2); smoothed vs raw comparison and its explanation (2);
recognising the grip-limit contamination (2).

### 1.6 [T] Attenuation bias

With $y = \theta x + e$ and observed $\tilde x = x + u$ ($u$ independent of $x$ and $e$),

$$\hat\theta = \frac{\sum\tilde x y}{\sum\tilde x^2}\ \xrightarrow{\ N\to\infty\ }\
\frac{\operatorname{cov}(\tilde x, y)}{\operatorname{var}(\tilde x)}
= \frac{\theta\sigma_x^2}{\sigma_x^2 + \sigma_u^2}.$$

The estimate is biased toward zero by the reliability ratio $\sigma_x^2/(\sigma_x^2+\sigma_u^2)$, and
more data does not help. Remedies: reduce $\sigma_u$ (smoothing, better sensors), use instrumental
variables (e.g. the *commanded* input, which is noise-free and correlated with $x$), or fit in a
domain where the noisy quantity is not a regressor.

### 1.7 [S] Identification without motion capture

**Model answer.**

| Quantity | Ground-truth signal | Error model and mitigation |
|---|---|---|
| Speed | wheel encoders, scale calibrated by rolling a measured 20 m line | slip under acceleration: calibrate at constant low speed; use undriven front wheels if instrumented |
| Yaw rate | IMU gyro | bias from stationary averaging (Lecture 3 §7); scale factor from a measured 10-turn spin |
| Lateral acceleration | $v\dot\psi$ in steady turns (not the accelerometer, which sees gravity through roll) | radius check against a chalk circle |
| Grip limit | the plateau of $v\dot\psi$ in increasing-speed constant-steer runs | repeat in both directions |
| Steering lag | camera-observed heading or gyro response to a commanded step | fit as in 1.5, at low $a_y$ to avoid saturation |

**Repetitions.** If one trial estimates a parameter with coefficient of variation $c$, a 5% standard
error needs $n = (c/0.05)^2$ trials: $c = 20\%$ gives 16 trials. Strong answers state $c$ from a
pilot run rather than assuming it, and randomise the order of conditions (battery voltage drifts
during a session).

**Rubric.** Signals and error models (4); a calibration step for each (2); sample-size argument (2);
experimental-design hygiene (randomisation, both directions, battery) (2).
