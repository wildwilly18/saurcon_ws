# Chapter 1 — Vehicle Modelling and System Identification

**Notebook:** [01_bicycle_model_and_sysid.ipynb](notebooks/01_bicycle_model_and_sysid.ipynb)

## Learning objectives

- Derive Ackermann steering geometry and the kinematic bicycle model.
- State the assumptions of the kinematic model and the speed at which they break.
- Model the friction (grip) limit and actuator limits.
- Identify model parameters from logged data, and recognise when the "plant" itself is wrong.

## 1. Ackermann steering

When a car turns without tyre slip, every wheel rolls about a common
**instantaneous centre of rotation (ICR)** on the extension of the rear axle. For a
wheelbase $L$, track $T$ and turn radius $R$ (to the rear-axle centre), the inner
and outer front wheels need different angles:

$$\tan\delta_\text{in} = \frac{L}{R - T/2}, \qquad \tan\delta_\text{out} = \frac{L}{R + T/2}.$$

A linkage that achieves this is an *Ackermann linkage*. Gazebo's
`AckermannSteering` plugin computes the two angles for us and drives the steering
joints with a P-controller (`steer_p_gain`).

## 2. The kinematic bicycle model

Collapse each axle into a single wheel on the centreline. With the reference point
at the rear axle (our `base_link`), heading $\psi$, speed $v$ and front steering
angle $\delta$:

$$\dot x = v\cos\psi, \qquad \dot y = v\sin\psi, \qquad \dot\psi = \frac{v}{L}\tan\delta.$$

Choosing the rear axle makes the velocity point exactly along the heading — there is
no sideslip term — which is why `base_link` sits there. The yaw rate is
$r = v\tan\delta / L$ and the lateral (centripetal) acceleration is

$$a_y = v\, r = \frac{v^2}{L}\tan\delta = \frac{v^2}{R}.$$

**Assumptions:** no tyre slip, planar motion, instant steering. They hold while
$|a_y|$ is well below the friction limit.

## 3. Limits that matter for racing

**Grip (friction circle).** Tyres can supply at most about $\mu N$ of horizontal
force, so $\sqrt{a_x^2 + a_y^2} \le \mu g$. For a corner of curvature
$\kappa = 1/R$ the fastest steady speed is

$$v_\text{max}(\kappa) = \sqrt{\mu g / |\kappa|}.$$

On the racetrack's 2 m bends with $\mu g \approx 10\ \text{m/s}^2$, that is about
4.5 m/s. Beyond the limit the kinematic model is wrong: the Gazebo car oversteers
and spins (slip angles of 35–100° in the identification data).

**Actuators.** The drive is rate-limited (the plugin ramps speed at a fixed
acceleration) and the steering has a lag. In the fast training model we use

$$\dot v = \operatorname{clip}\!\left(\frac{v_\text{cmd}-v}{\Delta t},\, -b,\, a\right), \qquad
\dot\delta = \frac{\delta_\text{cmd} - \delta}{\tau_\delta}.$$

## 4. System identification

A model is only useful if its parameters match the plant. The procedure in
`src/saurcon_rl/saurcon_rl/sysid.py`:

1. Put the car on an empty floor (`config/sysid.world`) so nothing interferes.
2. Apply designed inputs: a full-throttle run and a braking stop (acceleration,
   braking), a steering step (lag), and a grid of constant speed × steering angle
   holds (steady-state yaw rate and the grip limit).
3. Record **ground truth** pose, differentiate for speed and yaw rate, and compare
   to the model's prediction.

Measured on the Gazebo car: traction-limited acceleration 4.1 m/s² and braking
4.5 m/s² (the drive plugin then ramped at 5 m/s², so the wheels slipped — see
chapter 6, section 6; the ramps are now 3.8 and 4.0 m/s²), steady yaw
rate within 2% of the bicycle model at 3 m/s, and a lateral grip limit of about
10 m/s² (sliding plateau median 9.8 m/s², quartiles 7.5–11.4). The notebook reproduces these numbers from `docs/course/data/sysid.csv`.

## 5. Case study — when identification finds a bug in the plant

The first identification run showed a top speed of **1.7 m/s regardless of the
command**, and almost no turning above 3 m/s. A focused test printed wheel speeds:
the driven rear wheels spun at the commanded rate (152 rad/s for 5 m/s), but the
free front wheels turned at only 50 rad/s. The rear tyres were slipping.

The cause was in the car model: each wheel joint had a viscous damping of
0.01 N·m·s/rad. Damping torque is $c\,\omega$; at 50 rad/s that is 0.5 N·m, which on
a 33 mm wheel is a **15 N** drag force per front wheel — as much as the rear tyres'
entire grip. The car reached the speed where drag equals traction and stopped
accelerating. Reducing the damping 100× gives about 1 N per wheel at 10 m/s, and
the car then followed any commanded speed.

**Lessons.** Units hide scale: a "small" damping coefficient is not small on a small
wheel. And identification is also verification — if the data looks physically odd,
check the model before fitting it.

## How SAURCON does it

| Concept | Where |
|---|---|
| Car geometry, joints, plugin | `src/middle_earth/models/rc_ackermann_vehicle/model.sdf` |
| Identification drive | `src/saurcon_rl/saurcon_rl/sysid.py` |
| Fast model used for RL | `src/saurcon_rl/saurcon_rl/env.py` (`RaceEnv.step`) |
| Wheel-speed odometry in sim | `src/saurcon_rc/src/sim_saurcon_rc.cpp` (`joint_state_cb`) |

## Exercises

1. ★ Compute $\delta_\text{in}$ and $\delta_\text{out}$ for SAURCON at $R = 2$ m.
2. ★ Using $v_\text{max}(\kappa)$, estimate the minimum lap time of the racetrack if the car could change speed instantly. Then add the 4.1 / 4.5 m/s² limits (notebook 05 does this numerically).
3. ★★ The kinematic model has no sideslip. Derive the *dynamic* bicycle model with linear tyre cornering stiffness and find the speed at which its yaw-rate gain departs 10% from the kinematic one.
4. ★★ In the notebook, fit the steering time constant $\tau_\delta$ by least squares on the steering-step data.
5. ★★★ Design an identification experiment for the real car that needs no motion capture. Which signals do you trust for ground truth?
