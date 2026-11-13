# Chapter 7 — Experimental Method

## Learning objectives

- Measure a robotic system against ground truth with the right alignment and metrics.
- Isolate runs so results are not contaminated by other processes.
- Report results honestly: single runs, coverage, failures, and what was not tested.

## 1. Ground truth and alignment

Simulation gives exact ground truth (`/world/<name>/dynamic_pose/info`).
SAURCON's `scripts/sim_eval/gt_bridge.py` republishes the car's pose with the
simulator's timestamp — the standard bridge dropped timestamps, which made early
comparisons wrong by the message latency.

Estimates live in their own frames (`odom`, `map`). Align them to the world with
**one** SE(2) transform fixed at the start (or taken from the mapping run for
localization), never a best-fit over the whole trajectory: a best fit hides
initialisation errors and drift.

Remember what the reference point is: ground truth is the model origin, 0.127 m
ahead of `base_link`; forgetting that is a 13 cm error at every sample.

## 2. Metrics

- **Position RMS and maximum** over a stated window (driving only — not the parked
  warm-up, not the controller-loss test at the end).
- **Heading RMS**, with angles wrapped.
- **Coverage**: largest gap between samples and the duration actually observed. A
  short surviving segment with good RMS is a failure, not a result (the visual-
  odometry fallback "scored" 4 m RMS on 7 s of a 47 s lap).
- **Consistency**: fraction of errors inside the filter's own ±3σ.
- For racing: standing and flying lap times, gates passed, cones disturbed
  (`scripts/sim_eval/cone_watch.py`).

## 3. Isolation

Every run in `scripts/sim_eval/runsim.sh`:

- uses a fresh output directory (it refuses to overwrite);
- takes a workspace lock so two evaluations cannot overlap;
- sets a unique `GZ_PARTITION` and a separate `ROS_DOMAIN_ID`;
- starts each component in its own process group and cleans up only those groups.

**Case studies.** A failed launch left a second Gazebo running; its topics merged
with the next run. A test that killed `ros2 run` left the actual node processes
alive, doubling every TF message. A cleanup using `pkill -f <pattern>` killed the
shell running it, because the shell's own command line matched — and, later, a
similar pattern also matched a *training run's* wrapper, ending a smooth-reward
training run partway (chapter 9, section 10). Kill by recorded process ID or process
group, never by pattern. Child processes that must not outlive their parent (the
Gazebo servers of `gazebo_cone_env.py`) are started with `PR_SET_PDEATHSIG`. In each
case the symptom was a plausible-looking but wrong result.

## 3a. Testing safety logic without the robot

Watchdogs and freshness checks run rarely and fail silently. Test them as functions
of time with every collaborator faked: a clock you advance by hand, a TF buffer that
returns a transform at a chosen stamp (or raises), a policy that always says "full
speed", and a publisher that records commands
(`src/saurcon_rl/test/test_input_watchdogs.py`). Each test states one property
("expired odometry → zero command") and nothing is actuated. Check that a new test
fails on the old code before trusting that it passes on the new.

## 4. Reporting

- State **single run vs. repeated**; with one seed, say so and avoid claiming
  statistical significance.
- Report what failed alongside what passed (e.g., reverse relocalization from an
  unknown pose).
- Say what was not tested: here, no real-vehicle validation, and sim depth that is
  cleaner than real stereo.
- Keep raw logs and the exact command lines (`environment.txt`, `launch.log`,
  `log.csv`) with every result.
- Report **reliability as a count**: the classical follower with RTAB-Map running was
  first clean in 1 of 3 runs; reporting only the clean run's lap times would have
  hidden the problem that led to two bug fixes.
- When a bug in shared code is found, say which earlier results it affects (chapter 9,
  failure 5: every earlier ROS-stack cone result was obtained with mispaired depth).

## Exercises

1. ★ Score a run twice: once with start-pose alignment, once with a least-squares trajectory fit. Explain the difference.
2. ★★ Repeat the UKF marker-free run with 5 seeds. Report mean and spread; is the earlier single-run claim still supported?
3. ★★ Write a check that fails a run if more than one `gz sim` process is alive at start.
