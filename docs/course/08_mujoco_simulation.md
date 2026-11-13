# Chapter 8 — Physics Simulation with MuJoCo

**Notebooks:** [06_mujoco_fundamentals.ipynb](notebooks/06_mujoco_fundamentals.ipynb),
[07_mujoco_sim_to_sim.ipynb](notebooks/07_mujoco_sim_to_sim.ipynb)

## Learning objectives

- Read and write MJCF: bodies, joints, geoms, sites, actuators, defaults and collision filtering.
- Explain MuJoCo's generalised coordinates, soft-contact model, friction cones and implicit integration.
- Model a wheeled vehicle so that rolling contact is stable and actuators behave like real drives.
- Calibrate one simulator against another, and use a simulator to *predict* failures before they happen.
- Decide when a fast surrogate, a rigid-body simulator, or a full robotics simulator is the right tool.

## 1. Where MuJoCo fits

SAURCON now has three simulators of the same car:

| Simulator | Speed (control steps/s/core) | What it models | Used for |
|---|---|---|---|
| Bicycle model (`env.py`) | ~5,800 | kinematics, ramp limits, a friction-circle rule | fast experiments, pre-training |
| MuJoCo (`mujoco_env.py`) | ~1,000 | rigid bodies, tyre contacts, weight transfer, slip | training the racing policy |
| Gazebo (`full_sim`) | ~20 (real time, with sensors) | physics + camera, IMU, ROS 2, RTAB-Map, state machine | full-loop validation |
| Gazebo, lock-step (`gazebo_cone_env.py`) | ~37 per server (headless, camera rendered) | Gazebo physics and camera, real detector, no ROS | fine-tuning the cone policy (chapter 9) |

MuJoCo (Multi-Joint dynamics with Contact) is a physics engine built for control and
learning: fast, deterministic, with smooth contact dynamics and analytical
derivatives. It has no ROS integration or sensor pipeline of its own, which is why it
complements rather than replaces Gazebo here.

## 2. MJCF in one page

A model is an XML tree. The essentials:

```xml
<mujoco model="saurcon_raceway">
  <option timestep="0.002" integrator="implicitfast"/>
  <default> <default class="wheel"> <geom type="ellipsoid" .../> </default> </default>
  <worldbody>
    <geom name="floor" type="plane" .../>
    <body name="car" pos="0 0 0.006">
      <freejoint/>                                    <!-- 6 DoF -->
      <geom name="chassis" type="box" mass="4.0" .../>
      <site name="base_link" pos="-0.127 0 0.037"/>    <!-- a frame, no physics -->
      <body name="left_rear_wheel" ...>
        <joint type="hinge" axis="0 1 0"/>             <!-- 1 DoF -->
        <geom class="wheel" mass="0.3"/>
      </body> ...
    </body>
  </worldbody>
  <actuator>
    <velocity joint="left_rear_spin" kv="1" forcerange="-2 2"/>
    <position joint="left_steer" kp="4"/>
  </actuator>
</mujoco>
```

- **Bodies** form a kinematic tree; **joints** add degrees of freedom between a body and
  its parent. The state is $(q, \dot q)$ in *generalised* coordinates (here 7 + 6
  numbers for the free chassis plus one per wheel and knuckle), not one pose per body.
- **Geoms** carry shape, mass (if given) and contact properties. Inertia is computed
  from geoms automatically.
- **Sites** are named frames for sensing (our `base_link`).
- **Actuators** map controls to joint forces: `motor` (torque), `position`
  ($\tau = k_p(u - q)$), `velocity` ($\tau = k_v(u - \dot q)$), with optional
  `forcerange` limits.
- **Collision filtering**: two geoms collide when
  `(contype₁ & conaffinity₂) || (contype₂ & conaffinity₁)`. SAURCON's chassis never
  touches the floor; its wheels do; cones touch everything.

SAURCON generates the MJCF in Python (`saurcon_rl/mujoco_model.py`) so geometry stays
in one place and the cones come from the same world files as Gazebo.

## 3. Contact and friction

MuJoCo treats contact as a **soft constraint**: penetration produces a force through
a spring–damper whose stiffness and damping come from `solref` (time constant,
damping ratio) and `solimp` (impedance). This keeps the dynamics smooth and the
solver convex, at the price of small, tunable penetration.

Friction is a **cone** with `condim` dimensions: 1 = frictionless, 3 = sliding
friction, 4 = plus torsional (spinning) friction, 6 = plus rolling friction.
Wheels use `condim="4"`. When two geoms touch, MuJoCo uses the larger of their
friction coefficients by default.

**Engines differ.** Gazebo's ODE-based physics approximates the friction cone with
a *pyramid*, which permits more horizontal force in diagonal directions. With the
same nominal μ = 1.0, Gazebo's car cornered at ~10 m/s² while MuJoCo's managed
~7.5 m/s². MuJoCo's tyre friction was therefore **calibrated** to 1.4 to match
Gazebo's grip plateau (notebook 07). Never assume a parameter means the same thing
in two simulators — measure the behaviour.

## 4. Integration and time step

`implicitfast` treats velocity-dependent forces (damping, velocity actuators)
implicitly, which keeps stiff drives stable at larger steps. SAURCON uses a 2 ms step
(25 physics steps per 50 ms control step). The drive replicates Gazebo's
`AckermannSteering` plugin: the commanded speed is ramped at the acceleration and
braking limits, each rear wheel gets a velocity target with the plugin's
differential, and the knuckles get Ackermann angles (chapter 1).

## 5. Case studies from building the model

**The hopping car — and the wrong culprit.** In the first model the car accelerated
to 7 m/s, then its wheel contacts flickered between 0, 4 and 8, the chassis lifted
and it tumbled. Two changes fixed it at once: cylinder wheels became ellipsoids, and
the drive's velocity gain fell from 5 to 1. The cylinder got the blame. Testing the
four combinations afterwards (notebook 06) showed the opposite: with gain 1 both
shapes roll perfectly; with gain 5 *both* fail, the ellipsoid car worst of all
(it leapt 156 mm). The cause was the drive: a velocity actuator with a high gain on
a very light wheel slams its torque between the ±2 N·m limits every step, and the
car hops. **Change one variable at a time**, or re-test each change separately
before writing down why something works. Ellipsoids were kept because they give a
single smooth contact point.

**Friction calibration.** A sweep against the Gazebo identification data, scored only
on the steady 2–3 m/s rows (above that both cars spin): RMS lateral-acceleration error
1.40, **0.72**, 0.87 and 1.24 m/s² for μ = 1.2, **1.4**, 1.6, 1.8. The first attempt
scored all rows, spins included, and preferred 1.8 — a reminder that the metric decides
the answer. μ = 1.4 is also slightly under Gazebo's grip on average, the safe side for
training.

**A simulator that predicts a failure.** A policy fine-tuned in the bicycle model
with a friction-circle rule lapped cleanly there (7.6 s). In MuJoCo it spun on the
straight before the first bend: with only 0.04 rad of steering while braking at
6.7 m/s, the yaw rate reached 1.5–2 rad/s, nearly double the steering's kinematic
value — *brake-induced oversteer*, because only the rear wheels brake and their grip
is used up. The bicycle model cannot represent this. Raced in Gazebo, the same
policy spun out on its first lap. MuJoCo's prediction was right; the surrogate's was
not. That is the argument for training in MuJoCo.

| Policy | Bicycle model | MuJoCo | Gazebo full loop |
|---|---|---|---|
| Original (lateral grip only) | spins at 8.9 m | spins at 12 m | spun in the far bend |
| Fine-tuned with friction circle | 7.6 s lap, clean | spins at 12 m | spun at the end of the first bend |

## 6. Training in MuJoCo

`MujocoRaceEnv` inherits from `RaceEnv`: same observation, action, reward, termination
and randomisation (plus friction ×0.85–1.05 and mass ×0.9–1.1), so the same policy
network and the same ROS node work everywhere. A spin is detected physically —
sideslip above 25° at speed, or roll — rather than by a rule.

```bash
.venv-rl/bin/python -m saurcon_rl.train --env mujoco --out rl_runs/ppo_mj1 \
    --resume rl_runs/ppo_v2/best_model.zip --steps 12000000
```

Results of MuJoCo training and the Gazebo validation are recorded in
`src/saurcon_rl/README.md`.

The cone environment (`MujocoConeEnv`, chapter 9) adds two things the real car
imposes: a **steering slew limit** of 8 rad/s, the MG90S servo's speed, applied to the
action before it reaches the knuckles, and the smooth-driving penalty of chapter 9,
section 10. Model
the actuator you will have, or the policy learns to use one you do not.

**Looking like the real car.** The car's *visual* geoms were restyled after
photographs of the real vehicle (open tray with the battery, deck on standoffs,
compute box, the OAK-D in its cradle, MG90S servo, red bumper truss, three-spoke
wheels). They are visual only (`contype=0`, no mass), so the physics (5.4 kg) is
unchanged. Two checks belong with any such change: render the onboard camera and
count pixels belonging to the car (must be 0, or the detector sees its own bumper),
and run the detector on an empty floor (must find no cones).

**Going faster.** MJX runs MuJoCo in JAX on a GPU with thousands of environments in
parallel. It requires the environment to be written in JAX (no Python loops per
step), which is a natural follow-on project.

## How SAURCON does it

| Concept | Where |
|---|---|
| MJCF generator, Ackermann angles | `src/saurcon_rl/saurcon_rl/mujoco_model.py` |
| Environment | `src/saurcon_rl/saurcon_rl/mujoco_env.py` |
| Identification drive (Gazebo and MuJoCo) | `src/saurcon_rl/saurcon_rl/sysid.py` (`--mujoco`) |
| Side-by-side comparison | `src/saurcon_rl/saurcon_rl/sysid_compare.py` |

## Exercises

1. ★ In notebook 06, change the floor friction to 0.5 and repeat the sliding-block experiment. Which friction does MuJoCo use for the contact?
2. ★ Reduce the time step to 0.5 ms. Does the straight-line run change? What does it cost?
3. ★★ Add front-wheel braking (a velocity actuator on the front wheels during braking only) and show that brake-induced oversteer disappears.
4. ★★ Fit `solref` so that the MuJoCo car's slip angle at 3 m/s and 0.3 rad matches Gazebo's.
5. ★★★ Port `MujocoRaceEnv.step` to MJX and measure environment throughput on the GPU.
6. ★★★ Use MuJoCo's analytical derivatives (`mj_forward` finite differences or `mjd_transitionFD`) to linearise the car around a steady turn, and compute its yaw stability margin with and without braking.
