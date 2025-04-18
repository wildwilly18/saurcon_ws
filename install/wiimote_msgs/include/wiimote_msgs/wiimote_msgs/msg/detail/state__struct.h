// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/state.h"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__STATE__STRUCT_H_
#define WIIMOTE_MSGS__MSG__DETAIL__STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'INVALID'.
/**
  * Note: For ease of manipulation this message often uses
  *       int8[] when a bit vector would work. One might
  *       wish to use uint8[], but then Python takes
  *       the respective structure as a string and disallows
  *       item assignment.
 */
enum
{
  wiimote_msgs__msg__State__INVALID = -1
};

/// Constant 'INVALID_FLOAT'.
static const float wiimote_msgs__msg__State__INVALID_FLOAT = -1.0f;

/// Constant 'MSG_BTN_1'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_1 = 0
};

/// Constant 'MSG_BTN_2'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_2 = 1
};

/// Constant 'MSG_BTN_A'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_A = 2
};

/// Constant 'MSG_BTN_B'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_B = 3
};

/// Constant 'MSG_BTN_PLUS'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_PLUS = 4
};

/// Constant 'MSG_BTN_MINUS'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_MINUS = 5
};

/// Constant 'MSG_BTN_LEFT'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_LEFT = 6
};

/// Constant 'MSG_BTN_RIGHT'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_RIGHT = 7
};

/// Constant 'MSG_BTN_UP'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_UP = 8
};

/// Constant 'MSG_BTN_DOWN'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_DOWN = 9
};

/// Constant 'MSG_BTN_HOME'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_HOME = 10
};

/// Constant 'MSG_BTN_Z'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_Z = 0
};

/// Constant 'MSG_BTN_C'.
enum
{
  wiimote_msgs__msg__State__MSG_BTN_C = 1
};

/// Constant 'MSG_CLASSIC_BTN_X'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_X = 0
};

/// Constant 'MSG_CLASSIC_BTN_Y'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_Y = 1
};

/// Constant 'MSG_CLASSIC_BTN_A'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_A = 2
};

/// Constant 'MSG_CLASSIC_BTN_B'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_B = 3
};

/// Constant 'MSG_CLASSIC_BTN_PLUS'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_PLUS = 4
};

/// Constant 'MSG_CLASSIC_BTN_MINUS'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_MINUS = 5
};

/// Constant 'MSG_CLASSIC_BTN_LEFT'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_LEFT = 6
};

/// Constant 'MSG_CLASSIC_BTN_RIGHT'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_RIGHT = 7
};

/// Constant 'MSG_CLASSIC_BTN_UP'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_UP = 8
};

/// Constant 'MSG_CLASSIC_BTN_DOWN'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_DOWN = 9
};

/// Constant 'MSG_CLASSIC_BTN_HOME'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_HOME = 10
};

/// Constant 'MSG_CLASSIC_BTN_L'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_L = 11
};

/// Constant 'MSG_CLASSIC_BTN_R'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_R = 12
};

/// Constant 'MSG_CLASSIC_BTN_ZL'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_ZL = 13
};

/// Constant 'MSG_CLASSIC_BTN_ZR'.
enum
{
  wiimote_msgs__msg__State__MSG_CLASSIC_BTN_ZR = 14
};

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'angular_velocity_zeroed'
// Member 'angular_velocity_raw'
// Member 'linear_acceleration_zeroed'
// Member 'linear_acceleration_raw'
// Member 'nunchuk_acceleration_zeroed'
// Member 'nunchuk_acceleration_raw'
#include "geometry_msgs/msg/detail/vector3__struct.h"
// Member 'ir_tracking'
#include "wiimote_msgs/msg/detail/ir_source_info__struct.h"
// Member 'zeroing_time'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/State in the package wiimote_msgs.
/**
  * Wiimote State message containing one complete Wiimote state
 */
typedef struct wiimote_msgs__msg__State
{
  /// -----------------------------
  ///  Header
  /// ----------------------
  std_msgs__msg__Header header;
  /// ----------------------
  ///  Gyro reading
  /// -----------------------------
  ///  In radians/sec. If reading is invalid,
  ///  for instance b/c no gyro is attached to the Wii, then
  ///  set first element of covariance to -1 (same as imu_data.msg):
  ///  Covariance matrix (roll, pitch, yaw) in radians^2/sec^2.
  geometry_msgs__msg__Vector3 angular_velocity_zeroed;
  geometry_msgs__msg__Vector3 angular_velocity_raw;
  double angular_velocity_covariance[9];
  /// ----------------------
  ///  Accelerometer reading
  /// -----------------------------
  ///  Acceleration in m/sec^2. Covariance matrix
  ///  (x,y,z) in m^2/sec^4.  (all same as imu_data.msg)
  geometry_msgs__msg__Vector3 linear_acceleration_zeroed;
  geometry_msgs__msg__Vector3 linear_acceleration_raw;
  double linear_acceleration_covariance[9];
  /// ------------------------------
  ///  Nunchuk Accelerometer reading
  /// ------------------------------
  geometry_msgs__msg__Vector3 nunchuk_acceleration_zeroed;
  geometry_msgs__msg__Vector3 nunchuk_acceleration_raw;
  /// -----------------
  ///  Nunchuk Joystick
  /// -----------------
  float nunchuk_joystick_zeroed[2];
  float nunchuk_joystick_raw[2];
  /// ----------------------
  ///  Wiimote buttons
  /// -----------------------------
  ///  Mappings from Wiimote button name
  ///  to array position are defined above.
  bool buttons[11];
  bool nunchuk_buttons[2];
  /// ----------------------
  ///  Wiimote LED states:
  /// -----------------------------
  bool leds[4];
  /// ----------------------
  ///  Wiimote Rumble
  /// -----------------------------
  ///  State (True or False)
  bool rumble;
  /// ----------------------
  ///  IR Light sensor (Camera)
  /// -----------------------------
  ///  The Wiimote handles up to four light sources,
  ///  and the wiimote_controller software is written to
  ///  that limit as well. For future expansion
  ///  we make the following array extensible, rather
  ///  than locking its length down to four:
  wiimote_msgs__msg__IrSourceInfo__Sequence ir_tracking;
  /// ----------------------
  ///  Wiimote battery
  /// -----------------------------
  ///  A battery reading consists of two numbers:
  ///  the battery percentage, and the raw reading.
  ///  Maximum battery is 208 units (unknown how this
  ///  relates to electrical properties):
  float raw_battery;
  float percent_battery;
  /// ----------------------
  ///  Time of most recent zeroing:
  /// -----------------------------
  builtin_interfaces__msg__Time zeroing_time;
  /// ----------------------
  ///  Error vector
  /// -----------------------------
  ///  For error condition definitions see wiimoteConstants.py
  ///  Value of zero means all is well. (Currently NOT used).
  uint64_t errors;
} wiimote_msgs__msg__State;

// Struct for a sequence of wiimote_msgs__msg__State.
typedef struct wiimote_msgs__msg__State__Sequence
{
  wiimote_msgs__msg__State * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wiimote_msgs__msg__State__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WIIMOTE_MSGS__MSG__DETAIL__STATE__STRUCT_H_
