# Lecture 5 — Solutions

### 5.1 [T] The state machine as a table

| State \ event | menu held 2 s | view held 2 s | joystick lost | RC lost | RC ready |
|---|---|---|---|---|---|
| STARTUP | — | — | — | — | → STANDBY |
| STANDBY | → RUN_CONTROL | → RUN_AUTONOMOUS | *?* | *?* | — |
| RUN_CONTROL | → STANDBY | → STANDBY | → FAULT | → FAULT | — |
| RUN_AUTONOMOUS | → STANDBY | → STANDBY | → FAULT | → FAULT | — |
| FAULT | *?* | → STANDBY | — | — | — |

Every transition clears the drive command. **Unspecified pairs** (*?*): joystick or RC lost in
STANDBY, and menu held in FAULT. Recommended: losing the joystick in STANDBY should *block* entry to
RUN states (stay in STANDBY, flag it) rather than fault, since nothing is moving; RC lost in STANDBY
should fault (the car's actuator side is unknown); menu held in FAULT should do nothing, so that only
the documented reset leaves FAULT. Also discuss STARTUP with RC never ready (a start-up timeout to FAULT).
Rubric: table (5), unspecified pairs found (3), justified choices (2).

### 5.2 [T] Heartbeat timeout

See the lecture's answer. Strong answers compute both sides: false faults per hour at 1 s
(≈ 0.05 × 3600 = 180) versus at 3 s (≈ 0.45 per hour), against a worst-case 3 s of undetected RC
failure.

### 5.3 [T] Stop vs. fault on command timeout

**For faulting:** the planner has failed, and failures should be sticky and require a human (§2); a
planner that oscillates between alive and dead would otherwise produce stop–go driving with no record.
**Against:** the command timeout also fires on *recoverable* stalls (a CPU spike, a slow simulation
step; Lecture 6 §6 records one), and a fault on every stall would make autonomy unusable; stopping
already removes the hazard in the table of §1 (drive commands continuing after the planner stops). A
good synthesis: stop on the first timeout, **fault after N timeouts in a window** (a rate-based
escalation), and log every event. Rubric: both sides with hazard references (6), a synthesis (4).

### 5.4 [C] State-machine test with an injected clock

**Approach.** The state machine reads `this->now()`, so either (a) run it with `use_sim_time:=true` and
publish `/clock` from the test, or (b) refactor the transition logic into a pure function
`next(state, inputs, now)` and test that directly. (b) is the better design and the expected answer.

```cpp
TEST(StateMachine, AutonomyFaultsOnJoystickLoss) {
  Logic sm;                          // pure transition logic, no ROS
  double t = 0;
  sm.on_rc_ready(t);                         EXPECT_EQ(sm.state(), STANDBY);
  for (; t < 2.1; t += 0.03) sm.tick(t, {.view = true, .joy_alive = true, .rc_alive = true});
  EXPECT_EQ(sm.state(), RUN_AUTONOMOUS);
  for (; t < 3.3; t += 0.03) sm.tick(t, {.joy_alive = false, .rc_alive = true});   // 1 s dead-man
  EXPECT_EQ(sm.state(), FAULT);
  EXPECT_EQ(sm.drive_command(), Zero);
  for (double t0 = t; t < t0 + 2.1; t += 0.03) sm.tick(t, {.view = true, .joy_alive = true, .rc_alive = true});
  EXPECT_EQ(sm.state(), STANDBY);
}
```

Also test that a 1.9 s hold does *not* transition, and that a hold started before a fault does not
count after it. Rubric: deterministic clock (4), the full path (3), the negative cases (3).

### 5.5 [C] Out-of-order images

**Reference solution** (passes against the current node; add it to `test_follower_node.py`):

```python
def test_follower_node_out_of_order_image(cone_node):
    all_fresh(cone_node)                                   # image captured at t = 100.0
    cone_node.step()
    assert cone_node.pub.msgs[-1][0] > 0
    cone_node.clock.t = 100.2
    cone_node.on_odom(odom_msg(100.2)); cone_node.tf.t = 100.2
    cone_node.detect(image(99.9), None)                    # an older image arrives late
    assert cone_node.last_image == 100.0                   # freshness did not go backwards...
    cone_node.detect(image(100.15), None)
    assert cone_node.last_image == 100.15                  # ...but a newer one advances it
    cone_node.clock.t = 100.46                             # 0.31 s after the newest capture
    cone_node.on_odom(odom_msg(100.46)); cone_node.tf.t = 100.46
    cone_node.step()
    assert cone_node.pub.msgs[-1] == (0.0, 0.0)            # stops on time
```

The fixture replaces `detect` with a stub that applies the same `max()` as the real method. A stronger
answer also calls the real `ConeFollowerNode.detect` with a fake detector and a fake `cv_bridge`, so
the property is tested on production code. **Note for instructors:** writing the predecessor of this
problem (recovery after a simulation clock reset) exposed a real bug: the node did not clear its cone
memory when the clock went backwards, so cones stamped in the "future" were never aged out. It is now
fixed, with a regression test, which makes it a good case study to discuss after the problem is due.

### 5.6 [T] Avoiding stop-start driving

See the lecture's answer. Full credit requires: (i) the bound (drive at most $T_\text{coast}$ after
the last image); (ii) the speed rule that keeps the hazard bounded, $v \le \sqrt{2b\,(\ell_\text{seen} -
v\,T_\text{coast})}$, i.e. able to stop within the path seen at the last image; (iii) the new hazard
(acting on stale cones, bounded by odometry drift over $T_\text{coast}$); (iv) a fake-clock test
showing the car coasts for less than $T_\text{coast}$ and then stops.

### 5.7 [T] ESP32-side safety

**Model answer.**

1. **Command timeout on the ESP32** (≈ 150–250 ms, independent of ROS): no valid command ⇒ throttle to
   neutral with active braking, steering held then centred.
2. **Sequence numbers and timestamps** on commands; reject duplicates and out-of-order packets, so a
   burst of delayed packets cannot replay old throttle.
3. **Heartbeat from the Pi**, separate from commands: loss ⇒ the ESP32's own FAULT state, which needs a
   physical action (RC transmitter switch or button) to clear.
4. **Hardware watchdog** on the ESP32, so a firmware hang resets it into a safe state (outputs default
   to neutral at boot).
5. **Independent RC override** (a transmitter channel the ESP32 always honours) as the final layer.

**Assumptions to state:** the ESP32's clock and firmware are correct; neutral PWM really means stopped
(calibrated ESC); power to the ESP32 outlives power to the motor driver; a brownout resets to safe
outputs. Rubric: timeout (2), replay protection (2), heartbeat/fault (2), watchdog (2), assumptions
stated (2).
