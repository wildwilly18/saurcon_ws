# Chapter 5 — Vehicle Software and Safety

## Learning objectives

- Design a mode state machine for a vehicle with manual and autonomous control.
- Implement dead-man switches, heartbeats and command timeouts, and reason about their failure modes.
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
