// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice
#include "wiimote_msgs/msg/detail/state__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "wiimote_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "wiimote_msgs/msg/detail/state__struct.h"
#include "wiimote_msgs/msg/detail/state__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "builtin_interfaces/msg/detail/time__functions.h"  // zeroing_time
#include "geometry_msgs/msg/detail/vector3__functions.h"  // angular_velocity_raw, angular_velocity_zeroed, linear_acceleration_raw, linear_acceleration_zeroed, nunchuk_acceleration_raw, nunchuk_acceleration_zeroed
#include "std_msgs/msg/detail/header__functions.h"  // header
#include "wiimote_msgs/msg/detail/ir_source_info__functions.h"  // ir_tracking

// forward declare type support functions

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_serialize_builtin_interfaces__msg__Time(
  const builtin_interfaces__msg__Time * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_deserialize_builtin_interfaces__msg__Time(
  eprosima::fastcdr::Cdr & cdr,
  builtin_interfaces__msg__Time * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t get_serialized_size_builtin_interfaces__msg__Time(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t max_serialized_size_builtin_interfaces__msg__Time(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_serialize_key_builtin_interfaces__msg__Time(
  const builtin_interfaces__msg__Time * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t get_serialized_size_key_builtin_interfaces__msg__Time(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t max_serialized_size_key_builtin_interfaces__msg__Time(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, builtin_interfaces, msg, Time)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_serialize_geometry_msgs__msg__Vector3(
  const geometry_msgs__msg__Vector3 * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_deserialize_geometry_msgs__msg__Vector3(
  eprosima::fastcdr::Cdr & cdr,
  geometry_msgs__msg__Vector3 * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t get_serialized_size_geometry_msgs__msg__Vector3(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t max_serialized_size_geometry_msgs__msg__Vector3(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_serialize_key_geometry_msgs__msg__Vector3(
  const geometry_msgs__msg__Vector3 * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t get_serialized_size_key_geometry_msgs__msg__Vector3(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t max_serialized_size_key_geometry_msgs__msg__Vector3(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, geometry_msgs, msg, Vector3)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_serialize_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_deserialize_std_msgs__msg__Header(
  eprosima::fastcdr::Cdr & cdr,
  std_msgs__msg__Header * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
bool cdr_serialize_key_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t get_serialized_size_key_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
size_t max_serialized_size_key_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_wiimote_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();

bool cdr_serialize_wiimote_msgs__msg__IrSourceInfo(
  const wiimote_msgs__msg__IrSourceInfo * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_wiimote_msgs__msg__IrSourceInfo(
  eprosima::fastcdr::Cdr & cdr,
  wiimote_msgs__msg__IrSourceInfo * ros_message);

size_t get_serialized_size_wiimote_msgs__msg__IrSourceInfo(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_wiimote_msgs__msg__IrSourceInfo(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_wiimote_msgs__msg__IrSourceInfo(
  const wiimote_msgs__msg__IrSourceInfo * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_wiimote_msgs__msg__IrSourceInfo(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_wiimote_msgs__msg__IrSourceInfo(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, wiimote_msgs, msg, IrSourceInfo)();


using _State__ros_msg_type = wiimote_msgs__msg__State;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wiimote_msgs
bool cdr_serialize_wiimote_msgs__msg__State(
  const wiimote_msgs__msg__State * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_std_msgs__msg__Header(
      &ros_message->header, cdr);
  }

  // Field name: angular_velocity_zeroed
  {
    cdr_serialize_geometry_msgs__msg__Vector3(
      &ros_message->angular_velocity_zeroed, cdr);
  }

  // Field name: angular_velocity_raw
  {
    cdr_serialize_geometry_msgs__msg__Vector3(
      &ros_message->angular_velocity_raw, cdr);
  }

  // Field name: angular_velocity_covariance
  {
    size_t size = 9;
    auto array_ptr = ros_message->angular_velocity_covariance;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: linear_acceleration_zeroed
  {
    cdr_serialize_geometry_msgs__msg__Vector3(
      &ros_message->linear_acceleration_zeroed, cdr);
  }

  // Field name: linear_acceleration_raw
  {
    cdr_serialize_geometry_msgs__msg__Vector3(
      &ros_message->linear_acceleration_raw, cdr);
  }

  // Field name: linear_acceleration_covariance
  {
    size_t size = 9;
    auto array_ptr = ros_message->linear_acceleration_covariance;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: nunchuk_acceleration_zeroed
  {
    cdr_serialize_geometry_msgs__msg__Vector3(
      &ros_message->nunchuk_acceleration_zeroed, cdr);
  }

  // Field name: nunchuk_acceleration_raw
  {
    cdr_serialize_geometry_msgs__msg__Vector3(
      &ros_message->nunchuk_acceleration_raw, cdr);
  }

  // Field name: nunchuk_joystick_zeroed
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_zeroed;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: nunchuk_joystick_raw
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_raw;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: buttons
  {
    size_t size = 11;
    auto array_ptr = ros_message->buttons;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: nunchuk_buttons
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_buttons;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: leds
  {
    size_t size = 4;
    auto array_ptr = ros_message->leds;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: rumble
  {
    cdr << (ros_message->rumble ? true : false);
  }

  // Field name: ir_tracking
  {
    size_t size = ros_message->ir_tracking.size;
    auto array_ptr = ros_message->ir_tracking.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      cdr_serialize_wiimote_msgs__msg__IrSourceInfo(
        &array_ptr[i], cdr);
    }
  }

  // Field name: raw_battery
  {
    cdr << ros_message->raw_battery;
  }

  // Field name: percent_battery
  {
    cdr << ros_message->percent_battery;
  }

  // Field name: zeroing_time
  {
    cdr_serialize_builtin_interfaces__msg__Time(
      &ros_message->zeroing_time, cdr);
  }

  // Field name: errors
  {
    cdr << ros_message->errors;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wiimote_msgs
bool cdr_deserialize_wiimote_msgs__msg__State(
  eprosima::fastcdr::Cdr & cdr,
  wiimote_msgs__msg__State * ros_message)
{
  // Field name: header
  {
    cdr_deserialize_std_msgs__msg__Header(cdr, &ros_message->header);
  }

  // Field name: angular_velocity_zeroed
  {
    cdr_deserialize_geometry_msgs__msg__Vector3(cdr, &ros_message->angular_velocity_zeroed);
  }

  // Field name: angular_velocity_raw
  {
    cdr_deserialize_geometry_msgs__msg__Vector3(cdr, &ros_message->angular_velocity_raw);
  }

  // Field name: angular_velocity_covariance
  {
    size_t size = 9;
    auto array_ptr = ros_message->angular_velocity_covariance;
    cdr.deserialize_array(array_ptr, size);
  }

  // Field name: linear_acceleration_zeroed
  {
    cdr_deserialize_geometry_msgs__msg__Vector3(cdr, &ros_message->linear_acceleration_zeroed);
  }

  // Field name: linear_acceleration_raw
  {
    cdr_deserialize_geometry_msgs__msg__Vector3(cdr, &ros_message->linear_acceleration_raw);
  }

  // Field name: linear_acceleration_covariance
  {
    size_t size = 9;
    auto array_ptr = ros_message->linear_acceleration_covariance;
    cdr.deserialize_array(array_ptr, size);
  }

  // Field name: nunchuk_acceleration_zeroed
  {
    cdr_deserialize_geometry_msgs__msg__Vector3(cdr, &ros_message->nunchuk_acceleration_zeroed);
  }

  // Field name: nunchuk_acceleration_raw
  {
    cdr_deserialize_geometry_msgs__msg__Vector3(cdr, &ros_message->nunchuk_acceleration_raw);
  }

  // Field name: nunchuk_joystick_zeroed
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_zeroed;
    cdr.deserialize_array(array_ptr, size);
  }

  // Field name: nunchuk_joystick_raw
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_raw;
    cdr.deserialize_array(array_ptr, size);
  }

  // Field name: buttons
  {
    size_t size = 11;
    auto array_ptr = ros_message->buttons;
    for (size_t i = 0; i < size; ++i) {
      uint8_t tmp;
      cdr >> tmp;
      array_ptr[i] = tmp ? true : false;
    }
  }

  // Field name: nunchuk_buttons
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_buttons;
    for (size_t i = 0; i < size; ++i) {
      uint8_t tmp;
      cdr >> tmp;
      array_ptr[i] = tmp ? true : false;
    }
  }

  // Field name: leds
  {
    size_t size = 4;
    auto array_ptr = ros_message->leds;
    for (size_t i = 0; i < size; ++i) {
      uint8_t tmp;
      cdr >> tmp;
      array_ptr[i] = tmp ? true : false;
    }
  }

  // Field name: rumble
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->rumble = tmp ? true : false;
  }

  // Field name: ir_tracking
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->ir_tracking.data) {
      wiimote_msgs__msg__IrSourceInfo__Sequence__fini(&ros_message->ir_tracking);
    }
    if (!wiimote_msgs__msg__IrSourceInfo__Sequence__init(&ros_message->ir_tracking, size)) {
      fprintf(stderr, "failed to create array for field 'ir_tracking'");
      return false;
    }
    auto array_ptr = ros_message->ir_tracking.data;
    for (size_t i = 0; i < size; ++i) {
      cdr_deserialize_wiimote_msgs__msg__IrSourceInfo(cdr, &array_ptr[i]);
    }
  }

  // Field name: raw_battery
  {
    cdr >> ros_message->raw_battery;
  }

  // Field name: percent_battery
  {
    cdr >> ros_message->percent_battery;
  }

  // Field name: zeroing_time
  {
    cdr_deserialize_builtin_interfaces__msg__Time(cdr, &ros_message->zeroing_time);
  }

  // Field name: errors
  {
    cdr >> ros_message->errors;
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wiimote_msgs
size_t get_serialized_size_wiimote_msgs__msg__State(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _State__ros_msg_type * ros_message = static_cast<const _State__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: angular_velocity_zeroed
  current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
    &(ros_message->angular_velocity_zeroed), current_alignment);

  // Field name: angular_velocity_raw
  current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
    &(ros_message->angular_velocity_raw), current_alignment);

  // Field name: angular_velocity_covariance
  {
    size_t array_size = 9;
    auto array_ptr = ros_message->angular_velocity_covariance;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: linear_acceleration_zeroed
  current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
    &(ros_message->linear_acceleration_zeroed), current_alignment);

  // Field name: linear_acceleration_raw
  current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
    &(ros_message->linear_acceleration_raw), current_alignment);

  // Field name: linear_acceleration_covariance
  {
    size_t array_size = 9;
    auto array_ptr = ros_message->linear_acceleration_covariance;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: nunchuk_acceleration_zeroed
  current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
    &(ros_message->nunchuk_acceleration_zeroed), current_alignment);

  // Field name: nunchuk_acceleration_raw
  current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
    &(ros_message->nunchuk_acceleration_raw), current_alignment);

  // Field name: nunchuk_joystick_zeroed
  {
    size_t array_size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_zeroed;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: nunchuk_joystick_raw
  {
    size_t array_size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_raw;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: buttons
  {
    size_t array_size = 11;
    auto array_ptr = ros_message->buttons;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: nunchuk_buttons
  {
    size_t array_size = 2;
    auto array_ptr = ros_message->nunchuk_buttons;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: leds
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->leds;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: rumble
  {
    size_t item_size = sizeof(ros_message->rumble);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ir_tracking
  {
    size_t array_size = ros_message->ir_tracking.size;
    auto array_ptr = ros_message->ir_tracking.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_wiimote_msgs__msg__IrSourceInfo(
        &array_ptr[index], current_alignment);
    }
  }

  // Field name: raw_battery
  {
    size_t item_size = sizeof(ros_message->raw_battery);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: percent_battery
  {
    size_t item_size = sizeof(ros_message->percent_battery);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: zeroing_time
  current_alignment += get_serialized_size_builtin_interfaces__msg__Time(
    &(ros_message->zeroing_time), current_alignment);

  // Field name: errors
  {
    size_t item_size = sizeof(ros_message->errors);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wiimote_msgs
size_t max_serialized_size_wiimote_msgs__msg__State(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Field name: header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: angular_velocity_zeroed
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: angular_velocity_raw
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: angular_velocity_covariance
  {
    size_t array_size = 9;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: linear_acceleration_zeroed
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: linear_acceleration_raw
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: linear_acceleration_covariance
  {
    size_t array_size = 9;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: nunchuk_acceleration_zeroed
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: nunchuk_acceleration_raw
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: nunchuk_joystick_zeroed
  {
    size_t array_size = 2;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: nunchuk_joystick_raw
  {
    size_t array_size = 2;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: buttons
  {
    size_t array_size = 11;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: nunchuk_buttons
  {
    size_t array_size = 2;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: leds
  {
    size_t array_size = 4;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: rumble
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: ir_tracking
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_wiimote_msgs__msg__IrSourceInfo(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: raw_battery
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: percent_battery
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: zeroing_time
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_builtin_interfaces__msg__Time(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: errors
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = wiimote_msgs__msg__State;
    is_plain =
      (
      offsetof(DataType, errors) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wiimote_msgs
bool cdr_serialize_key_wiimote_msgs__msg__State(
  const wiimote_msgs__msg__State * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_key_std_msgs__msg__Header(
      &ros_message->header, cdr);
  }

  // Field name: angular_velocity_zeroed
  {
    cdr_serialize_key_geometry_msgs__msg__Vector3(
      &ros_message->angular_velocity_zeroed, cdr);
  }

  // Field name: angular_velocity_raw
  {
    cdr_serialize_key_geometry_msgs__msg__Vector3(
      &ros_message->angular_velocity_raw, cdr);
  }

  // Field name: angular_velocity_covariance
  {
    size_t size = 9;
    auto array_ptr = ros_message->angular_velocity_covariance;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: linear_acceleration_zeroed
  {
    cdr_serialize_key_geometry_msgs__msg__Vector3(
      &ros_message->linear_acceleration_zeroed, cdr);
  }

  // Field name: linear_acceleration_raw
  {
    cdr_serialize_key_geometry_msgs__msg__Vector3(
      &ros_message->linear_acceleration_raw, cdr);
  }

  // Field name: linear_acceleration_covariance
  {
    size_t size = 9;
    auto array_ptr = ros_message->linear_acceleration_covariance;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: nunchuk_acceleration_zeroed
  {
    cdr_serialize_key_geometry_msgs__msg__Vector3(
      &ros_message->nunchuk_acceleration_zeroed, cdr);
  }

  // Field name: nunchuk_acceleration_raw
  {
    cdr_serialize_key_geometry_msgs__msg__Vector3(
      &ros_message->nunchuk_acceleration_raw, cdr);
  }

  // Field name: nunchuk_joystick_zeroed
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_zeroed;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: nunchuk_joystick_raw
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_raw;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: buttons
  {
    size_t size = 11;
    auto array_ptr = ros_message->buttons;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: nunchuk_buttons
  {
    size_t size = 2;
    auto array_ptr = ros_message->nunchuk_buttons;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: leds
  {
    size_t size = 4;
    auto array_ptr = ros_message->leds;
    cdr.serialize_array(array_ptr, size);
  }

  // Field name: rumble
  {
    cdr << (ros_message->rumble ? true : false);
  }

  // Field name: ir_tracking
  {
    size_t size = ros_message->ir_tracking.size;
    auto array_ptr = ros_message->ir_tracking.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      cdr_serialize_key_wiimote_msgs__msg__IrSourceInfo(
        &array_ptr[i], cdr);
    }
  }

  // Field name: raw_battery
  {
    cdr << ros_message->raw_battery;
  }

  // Field name: percent_battery
  {
    cdr << ros_message->percent_battery;
  }

  // Field name: zeroing_time
  {
    cdr_serialize_key_builtin_interfaces__msg__Time(
      &ros_message->zeroing_time, cdr);
  }

  // Field name: errors
  {
    cdr << ros_message->errors;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wiimote_msgs
size_t get_serialized_size_key_wiimote_msgs__msg__State(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _State__ros_msg_type * ros_message = static_cast<const _State__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_key_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: angular_velocity_zeroed
  current_alignment += get_serialized_size_key_geometry_msgs__msg__Vector3(
    &(ros_message->angular_velocity_zeroed), current_alignment);

  // Field name: angular_velocity_raw
  current_alignment += get_serialized_size_key_geometry_msgs__msg__Vector3(
    &(ros_message->angular_velocity_raw), current_alignment);

  // Field name: angular_velocity_covariance
  {
    size_t array_size = 9;
    auto array_ptr = ros_message->angular_velocity_covariance;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: linear_acceleration_zeroed
  current_alignment += get_serialized_size_key_geometry_msgs__msg__Vector3(
    &(ros_message->linear_acceleration_zeroed), current_alignment);

  // Field name: linear_acceleration_raw
  current_alignment += get_serialized_size_key_geometry_msgs__msg__Vector3(
    &(ros_message->linear_acceleration_raw), current_alignment);

  // Field name: linear_acceleration_covariance
  {
    size_t array_size = 9;
    auto array_ptr = ros_message->linear_acceleration_covariance;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: nunchuk_acceleration_zeroed
  current_alignment += get_serialized_size_key_geometry_msgs__msg__Vector3(
    &(ros_message->nunchuk_acceleration_zeroed), current_alignment);

  // Field name: nunchuk_acceleration_raw
  current_alignment += get_serialized_size_key_geometry_msgs__msg__Vector3(
    &(ros_message->nunchuk_acceleration_raw), current_alignment);

  // Field name: nunchuk_joystick_zeroed
  {
    size_t array_size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_zeroed;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: nunchuk_joystick_raw
  {
    size_t array_size = 2;
    auto array_ptr = ros_message->nunchuk_joystick_raw;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: buttons
  {
    size_t array_size = 11;
    auto array_ptr = ros_message->buttons;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: nunchuk_buttons
  {
    size_t array_size = 2;
    auto array_ptr = ros_message->nunchuk_buttons;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: leds
  {
    size_t array_size = 4;
    auto array_ptr = ros_message->leds;
    (void)array_ptr;
    size_t item_size = sizeof(array_ptr[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: rumble
  {
    size_t item_size = sizeof(ros_message->rumble);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ir_tracking
  {
    size_t array_size = ros_message->ir_tracking.size;
    auto array_ptr = ros_message->ir_tracking.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_key_wiimote_msgs__msg__IrSourceInfo(
        &array_ptr[index], current_alignment);
    }
  }

  // Field name: raw_battery
  {
    size_t item_size = sizeof(ros_message->raw_battery);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: percent_battery
  {
    size_t item_size = sizeof(ros_message->percent_battery);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: zeroing_time
  current_alignment += get_serialized_size_key_builtin_interfaces__msg__Time(
    &(ros_message->zeroing_time), current_alignment);

  // Field name: errors
  {
    size_t item_size = sizeof(ros_message->errors);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_wiimote_msgs
size_t max_serialized_size_key_wiimote_msgs__msg__State(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;
  // Field name: header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: angular_velocity_zeroed
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: angular_velocity_raw
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: angular_velocity_covariance
  {
    size_t array_size = 9;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: linear_acceleration_zeroed
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: linear_acceleration_raw
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: linear_acceleration_covariance
  {
    size_t array_size = 9;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  // Field name: nunchuk_acceleration_zeroed
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: nunchuk_acceleration_raw
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: nunchuk_joystick_zeroed
  {
    size_t array_size = 2;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: nunchuk_joystick_raw
  {
    size_t array_size = 2;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: buttons
  {
    size_t array_size = 11;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: nunchuk_buttons
  {
    size_t array_size = 2;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: leds
  {
    size_t array_size = 4;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: rumble
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: ir_tracking
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_wiimote_msgs__msg__IrSourceInfo(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: raw_battery
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: percent_battery
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: zeroing_time
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_builtin_interfaces__msg__Time(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: errors
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint64_t);
    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = wiimote_msgs__msg__State;
    is_plain =
      (
      offsetof(DataType, errors) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _State__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const wiimote_msgs__msg__State * ros_message = static_cast<const wiimote_msgs__msg__State *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_wiimote_msgs__msg__State(ros_message, cdr);
}

static bool _State__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  wiimote_msgs__msg__State * ros_message = static_cast<wiimote_msgs__msg__State *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_wiimote_msgs__msg__State(cdr, ros_message);
}

static uint32_t _State__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_wiimote_msgs__msg__State(
      untyped_ros_message, 0));
}

static size_t _State__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_wiimote_msgs__msg__State(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_State = {
  "wiimote_msgs::msg",
  "State",
  _State__cdr_serialize,
  _State__cdr_deserialize,
  _State__get_serialized_size,
  _State__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _State__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_State,
  get_message_typesupport_handle_function,
  &wiimote_msgs__msg__State__get_type_hash,
  &wiimote_msgs__msg__State__get_type_description,
  &wiimote_msgs__msg__State__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, wiimote_msgs, msg, State)() {
  return &_State__type_support;
}

#if defined(__cplusplus)
}
#endif
