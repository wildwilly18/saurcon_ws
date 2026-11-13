# Solutions Manual — Autonomous Racing Systems

*For instructors and teaching assistants. Do not distribute to students before the due date.*

Worked solutions to every problem at the end of Lectures 0–9, and guidance for the notebook
problems (N-numbers). Notation follows [the course notation](../notation.md); equation numbers
refer to the lectures.

| File | Problems |
|---|---|
| [L0](L0_solutions.md) | 0.1–0.5 System overview |
| [L1](L1_solutions.md) | 1.1–1.7 Vehicle modelling and identification |
| [L2](L2_solutions.md) | 2.1–2.6 Sensors and measurement models |
| [L3](L3_solutions.md) | 3.1–3.6 Nonlinear state estimation |
| [L4](L4_solutions.md) | 4.1–4.8 SLAM and localization |
| [L5](L5_solutions.md) | 5.1–5.7 Safety-critical software |
| [L6](L6_solutions.md) | 6.1–6.7 Reinforcement learning |
| [L7](L7_solutions.md) | 7.1–7.5 Experimental method |
| [L8](L8_solutions.md) | 8.1–8.6 MuJoCo |
| [L9](L9_solutions.md) | 9.1–9.9 Perception-driven racing |
| [Notebooks](notebook_problems.md) | N1.1–N9.4 |

## How the solutions are written

- **[T] theory problems** have complete derivations. Accept any correct route; the rubric
  lists the steps that must appear.
- **[C] computation problems** give the method, a reference implementation sketch, and the
  **reference result computed in this workspace**, with the command or notebook cell that
  produced it. Students' numbers will differ with seeds and implementation details; grade the
  method and the interpretation, and accept results within the stated tolerance.
- **[S] simulation and design problems** are open-ended. They give a model answer, the points
  a strong answer makes, and common errors.

Several reference results surprised the authors and are flagged **Teaching note**: the
expected answer is not the one the problem statement leads students to anticipate. Those make
the best discussion sections. In particular:

- **1.4.** The braking-weighted friction ellipse changes the racetrack's lap-time bound by less than 0.01 s.
- **3.2.** The UKF's predicted covariance stays positive definite for every α tried.
- **9.7.** Doubling the follower's lateral-acceleration budget causes no failures; the car is perception-limited.

## Grading guidance

Each problem is worth 10 points unless the problem set says otherwise. Use the rubric's split
between **method** (setting up the right model or experiment), **execution** (correct algebra,
working code), and **interpretation** (what the result means, its uncertainty, and its limits).
Interpretation is never worth less than 3 points. A correct number with no explanation of what
it implies earns at most 7.

For computational answers, require: the code (runnable), the number with units and an uncertainty
where one is meaningful, and one sentence on what would change it. For any claim about reliability
or performance from a few runs, require the interval of Lecture 7 §5; deduct 2 points if a claim
from $n \le 5$ runs is stated without one.

## Reproducing the reference results

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
export PYTHONPATH=$PWD/src/saurcon_plan:$PWD/src/saurcon_rl:$PYTHONPATH MUJOCO_GL=egl
.venv-rl/bin/python docs/course/solutions/reference_results.py      # 1.4, 2.2, 3.2, 6.1, 9.1, 9.5, 9.7
```

The script prints every computed number quoted in this manual. MuJoCo results (9.7) take a few
minutes. Gazebo-based answers quote runs recorded while the course was developed. The run names are
given so instructors can regenerate them with `scripts/sim_eval/cone_race.sh`.
