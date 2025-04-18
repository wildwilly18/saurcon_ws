// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/timed_switch.h"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__STRUCT_H_
#define WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'ON'.
enum
{
  wiimote_msgs__msg__TimedSwitch__ON = 1
};

/// Constant 'OFF'.
enum
{
  wiimote_msgs__msg__TimedSwitch__OFF = 0
};

/// Constant 'NO_CHANGE'.
enum
{
  wiimote_msgs__msg__TimedSwitch__NO_CHANGE = -2
};

/// Constant 'REPEAT'.
enum
{
  wiimote_msgs__msg__TimedSwitch__REPEAT = -1
};

/// Constant 'FOREVER'.
enum
{
  wiimote_msgs__msg__TimedSwitch__FOREVER = -1
};

// Include directives for member types
// Member 'pulse_pattern'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/TimedSwitch in the package wiimote_msgs.
/**
  * TimedSwitch allows sender to:
  *    o turn a switch on,
  *    o turn a switch off, and
  *    o repeat an on/off pattern forever or for a
  *          given number of times.
  * Fields (refer to definitions of constants in the definition body):
  *     o switch_mode:
  *         ON: turn on  (num_cycles and pulse_pattern fields are ignored)
  *        OFF: turn off (num_cycles and pulse_pattern fields are ignored)
  *  NO_CHANGE: leave LED in its current state
  *     REPEAT: repeat an on/off pattern for as long
  *             as is indicated in the num_cycles field. The
  *             pattern is defined in the pulse_pattern field.
  *
  *     o num_cycles:
  *          n>=0: run the pattern that is defined in pulse_pattern
  *                n times.
  *          n==FOREVER: run the pattern that is defined in pulse_pattern
  *                       until a new TimedSwitch message is sent.
  *
  *     o pulse_pattern:
  *          A series of time durations in fractions of a second. The
  *          first number is the duration for having the switch on.
  *          The second number is the duration for which the switch
  *          is off. The third is an 'on' period again, etc.
  *          A pattern is terminated with the end of the array.
  *
  *          Example: [1,1] specifies an on-off sequence of 1 second.
 */
typedef struct wiimote_msgs__msg__TimedSwitch
{
  int8_t switch_mode;
  int32_t num_cycles;
  rosidl_runtime_c__float__Sequence pulse_pattern;
} wiimote_msgs__msg__TimedSwitch;

// Struct for a sequence of wiimote_msgs__msg__TimedSwitch.
typedef struct wiimote_msgs__msg__TimedSwitch__Sequence
{
  wiimote_msgs__msg__TimedSwitch * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wiimote_msgs__msg__TimedSwitch__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__STRUCT_H_
