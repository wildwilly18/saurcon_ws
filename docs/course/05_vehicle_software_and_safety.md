# Chapter 5 — Vehicle Software and Safety

## Learning objectives

- Design a mode state machine for a vehicle with manual and autonomous control.
- Implement dead-man switches, heartbeats and command timeouts, and reason about their failure modes.
- Explain why a command timeout does not protect against a node driving on stale inputs, and add input-freshness checks.
- Recognise undefined behaviour and initialisation hazards in embedded C++.
- Plan safe hand-over between human and autonomy.

## 1. Why a state machine

A car that can be driven by a person, by software, or not at all needs an explicit,
small set of modes with defined transitions. SAURCON's (`saurcon_rc/src/state_machine.cpp`):

```
STARTUP ──(RC reports ready)──► STANDBY
STANDBY ──hold menu 2 s──► RUN_CONTROL      (joystick drives)
STANDBY ──hold view 2 s──► RUN_AUTONOMOUS   (policy drives, /auto_cmd)
RUN_*   ──hold menu or view 2 s──► STANDBY
RUN_*   ──heartbeat lost──► FAULT ──hold view 2 s──► STANDBY
```

The ESP32 runs its own matching state machine; the ROS side commands it on
`/rc_state_cmd` and listens to `/saurcon/state`. Drive commands leave on
`/ctrl_output` only in RUN states; otherwise a stop command is published every
30 ms.

**Design rules used:**

- Long presses (2 s) for every mode change, so a bumped button does nothing.
- Every state change clears the drive command and immediately tells the ESP32,
  rather than waiting for the 1 Hz status timer.
- A fault is sticky: it needs a deliberate human action to clear.

## 2. Watchdogs

| Watchdog | Timeout | Action |
|---|---|---|
| Joystick heartbeat (dead-man) | 1 s | FAULT from any RUN state |
| RC (ESP32) heartbeat | 3 s (status is 1 Hz) | FAULT |
| Autonomous command age | 0.25 s | stop (stay in RUN_AUTONOMOUS) |

In autonomy the joystick stays a **dead-man switch**: if the operator's controller
disconnects, the car stops even though the policy is still sending commands.

The table guards against a *silent* publisher. It cannot tell whether a publisher's
commands are based on current data, so each driving node also checks its own inputs:

| Node | Input | Timeout | Action |
|---|---|---|---|
| map policy (`policy_node.py`) | `/saurcon/nav_state` header stamp | 0.25 s (`state_timeout`) | zero command every step, history reset |
| cone node (`cone_policy_node.py`) | camera image capture stamp | 0.3 s (`image_timeout`) | zero command |
| cone node | odometry message stamp | 0.25 s (`odom_timeout`) | zero command |
| cone node | `odom → base_link` transform age / lookup | 0.25 s (`tf_timeout`) | zero command, cone memory cleared |

**Case study — a live publisher with dead inputs.** A review found that once the map
policy had received one navigation state, it kept computing and publishing commands
at 20 Hz forever: it checked only whether a state had *ever* arrived. If the estimator
crashed, every one of those commands refreshed the state machine's 0.25 s command
watchdog, so the car would have driven on a frozen pose at full speed. Reproduced
with a fake publisher: 200 consecutive commands at 6 m/s from one stored state. The
cone node had the same flaw in subtler forms: it clamped an arbitrarily old
transform's age to 0.2 s, used an identity pose if the lookup failed, and marked an
image fresh when it was *processed* rather than when it was *taken*.

Design rules that came out of it:

- **Judge freshness by the data's own timestamp**, not by when it arrived or was
  processed, and refuse stamps that are not newer than the last accepted one (a
  replayed message must not renew validity).
- **Stop by publishing zero**, not by going silent: the downstream watchdog then sees
  a deliberate stop rather than a lost link, and the operator sees a consistent state.
- **Never substitute a default for missing data** (an identity transform, a clamped
  age). Extrapolate over *bounded* normal latency only.
- **Reset history on recovery** (previous action, steering estimate, remembered
  cones), so the first command after an outage is not built on pre-outage state.
- **Test it with a fake clock** without actuating anything
  (`src/saurcon_rl/test/test_input_watchdogs.py`).

**Case study — the disabled watchdog.** In the original code the heartbeat check was
commented out. Losing the controller in RUN_CONTROL left the last stick position
latched — the car kept driving at that throttle indefinitely. Re-enabling it also
required fixing the timestamps it compared: a default-constructed `rclcpp::Time` has
a different clock type from `now()`, and subtracting the two throws. Watchdogs are
code that rarely runs; test them deliberately (the scripted lap ends with a
controller-loss test for this reason).

## 3. Undefined behaviour in a control loop

`menu_held` and several other members had no initial value and were read every
30 ms before any joystick message arrived. Depending on stack contents the car
could crash the node or jump straight to RUN_CONTROL. Give every member a default;
compile with warnings and sanitizers in CI. Bounds-check every array from the
outside world (`Joy.axes`, `JointState.velocity`): a different gamepad has a
different layout.

## 4. Hand-over between human and autonomy

The policy node publishes `/auto_cmd` continuously; the state machine ignores it
except in RUN_AUTONOMOUS. Entering autonomy is a deliberate 2 s hold, and the
operator can always take back control with a 2 s hold or by letting go of the
controller. When designing your own: decide what the car does on *every* edge —
entering, leaving, and every fault — and test each one.

## Exercises

1. ★ Draw the state machine above as a table of (state, event) → (next state, action). Which pairs are undefined?
2. ★ Why is the RC heartbeat timeout 3 s rather than 1 s?
3. ★★ The autonomous-command timeout stops the car but does not fault it. Argue for and against faulting instead.
4. ★★ Write a unit test that drives the state machine through STANDBY → RUN_AUTONOMOUS → (joystick lost) → FAULT → STANDBY using a fake clock.
5. ★★★ The micro-ROS link can drop packets. Design the ESP32-side behaviour so that the car is safe even if the Pi crashes mid-command.
6. ★★ The cone node stops for one control step whenever its newest image is older than 0.3 s; under SLAM load that happens on ~6% of steps. Propose a rule that keeps the safety property but avoids stop-start driving (hint: what does the car do between two images anyway?), and say how you would test it.
7. ★ Why does the map policy reject a state whose stamp equals the last accepted one? Give a failure that this prevents.
