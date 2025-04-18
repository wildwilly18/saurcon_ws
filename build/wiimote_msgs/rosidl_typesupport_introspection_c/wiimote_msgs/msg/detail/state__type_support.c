// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "wiimote_msgs/msg/detail/state__rosidl_typesupport_introspection_c.h"
#include "wiimote_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "wiimote_msgs/msg/detail/state__functions.h"
#include "wiimote_msgs/msg/detail/state__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `angular_velocity_zeroed`
// Member `angular_velocity_raw`
// Member `linear_acceleration_zeroed`
// Member `linear_acceleration_raw`
// Member `nunchuk_acceleration_zeroed`
// Member `nunchuk_acceleration_raw`
#include "geometry_msgs/msg/vector3.h"
// Member `angular_velocity_zeroed`
// Member `angular_velocity_raw`
// Member `linear_acceleration_zeroed`
// Member `linear_acceleration_raw`
// Member `nunchuk_acceleration_zeroed`
// Member `nunchuk_acceleration_raw`
#include "geometry_msgs/msg/detail/vector3__rosidl_typesupport_introspection_c.h"
// Member `ir_tracking`
#include "wiimote_msgs/msg/ir_source_info.h"
// Member `ir_tracking`
#include "wiimote_msgs/msg/detail/ir_source_info__rosidl_typesupport_introspection_c.h"
// Member `zeroing_time`
#include "builtin_interfaces/msg/time.h"
// Member `zeroing_time`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  wiimote_msgs__msg__State__init(message_memory);
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_fini_function(void * message_memory)
{
  wiimote_msgs__msg__State__fini(message_memory);
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__angular_velocity_covariance(
  const void * untyped_member)
{
  (void)untyped_member;
  return 9;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__angular_velocity_covariance(
  const void * untyped_member, size_t index)
{
  const double * member =
    (const double *)(untyped_member);
  return &member[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__angular_velocity_covariance(
  void * untyped_member, size_t index)
{
  double * member =
    (double *)(untyped_member);
  return &member[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__angular_velocity_covariance(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__angular_velocity_covariance(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__angular_velocity_covariance(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__angular_velocity_covariance(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__linear_acceleration_covariance(
  const void * untyped_member)
{
  (void)untyped_member;
  return 9;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__linear_acceleration_covariance(
  const void * untyped_member, size_t index)
{
  const double * member =
    (const double *)(untyped_member);
  return &member[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__linear_acceleration_covariance(
  void * untyped_member, size_t index)
{
  double * member =
    (double *)(untyped_member);
  return &member[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__linear_acceleration_covariance(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__linear_acceleration_covariance(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__linear_acceleration_covariance(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__linear_acceleration_covariance(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__nunchuk_joystick_zeroed(
  const void * untyped_member)
{
  (void)untyped_member;
  return 2;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_joystick_zeroed(
  const void * untyped_member, size_t index)
{
  const float * member =
    (const float *)(untyped_member);
  return &member[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_joystick_zeroed(
  void * untyped_member, size_t index)
{
  float * member =
    (float *)(untyped_member);
  return &member[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__nunchuk_joystick_zeroed(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_joystick_zeroed(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__nunchuk_joystick_zeroed(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_joystick_zeroed(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__nunchuk_joystick_raw(
  const void * untyped_member)
{
  (void)untyped_member;
  return 2;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_joystick_raw(
  const void * untyped_member, size_t index)
{
  const float * member =
    (const float *)(untyped_member);
  return &member[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_joystick_raw(
  void * untyped_member, size_t index)
{
  float * member =
    (float *)(untyped_member);
  return &member[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__nunchuk_joystick_raw(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_joystick_raw(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__nunchuk_joystick_raw(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_joystick_raw(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__buttons(
  const void * untyped_member)
{
  (void)untyped_member;
  return 11;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__buttons(
  const void * untyped_member, size_t index)
{
  const bool * member =
    (const bool *)(untyped_member);
  return &member[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__buttons(
  void * untyped_member, size_t index)
{
  bool * member =
    (bool *)(untyped_member);
  return &member[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__buttons(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const bool * item =
    ((const bool *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__buttons(untyped_member, index));
  bool * value =
    (bool *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__buttons(
  void * untyped_member, size_t index, const void * untyped_value)
{
  bool * item =
    ((bool *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__buttons(untyped_member, index));
  const bool * value =
    (const bool *)(untyped_value);
  *item = *value;
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__nunchuk_buttons(
  const void * untyped_member)
{
  (void)untyped_member;
  return 2;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_buttons(
  const void * untyped_member, size_t index)
{
  const bool * member =
    (const bool *)(untyped_member);
  return &member[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_buttons(
  void * untyped_member, size_t index)
{
  bool * member =
    (bool *)(untyped_member);
  return &member[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__nunchuk_buttons(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const bool * item =
    ((const bool *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_buttons(untyped_member, index));
  bool * value =
    (bool *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__nunchuk_buttons(
  void * untyped_member, size_t index, const void * untyped_value)
{
  bool * item =
    ((bool *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_buttons(untyped_member, index));
  const bool * value =
    (const bool *)(untyped_value);
  *item = *value;
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__leds(
  const void * untyped_member)
{
  (void)untyped_member;
  return 4;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__leds(
  const void * untyped_member, size_t index)
{
  const bool * member =
    (const bool *)(untyped_member);
  return &member[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__leds(
  void * untyped_member, size_t index)
{
  bool * member =
    (bool *)(untyped_member);
  return &member[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__leds(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const bool * item =
    ((const bool *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__leds(untyped_member, index));
  bool * value =
    (bool *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__leds(
  void * untyped_member, size_t index, const void * untyped_value)
{
  bool * item =
    ((bool *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__leds(untyped_member, index));
  const bool * value =
    (const bool *)(untyped_value);
  *item = *value;
}

size_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__ir_tracking(
  const void * untyped_member)
{
  const wiimote_msgs__msg__IrSourceInfo__Sequence * member =
    (const wiimote_msgs__msg__IrSourceInfo__Sequence *)(untyped_member);
  return member->size;
}

const void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__ir_tracking(
  const void * untyped_member, size_t index)
{
  const wiimote_msgs__msg__IrSourceInfo__Sequence * member =
    (const wiimote_msgs__msg__IrSourceInfo__Sequence *)(untyped_member);
  return &member->data[index];
}

void * wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__ir_tracking(
  void * untyped_member, size_t index)
{
  wiimote_msgs__msg__IrSourceInfo__Sequence * member =
    (wiimote_msgs__msg__IrSourceInfo__Sequence *)(untyped_member);
  return &member->data[index];
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__ir_tracking(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const wiimote_msgs__msg__IrSourceInfo * item =
    ((const wiimote_msgs__msg__IrSourceInfo *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__ir_tracking(untyped_member, index));
  wiimote_msgs__msg__IrSourceInfo * value =
    (wiimote_msgs__msg__IrSourceInfo *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__ir_tracking(
  void * untyped_member, size_t index, const void * untyped_value)
{
  wiimote_msgs__msg__IrSourceInfo * item =
    ((wiimote_msgs__msg__IrSourceInfo *)
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__ir_tracking(untyped_member, index));
  const wiimote_msgs__msg__IrSourceInfo * value =
    (const wiimote_msgs__msg__IrSourceInfo *)(untyped_value);
  *item = *value;
}

bool wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__resize_function__State__ir_tracking(
  void * untyped_member, size_t size)
{
  wiimote_msgs__msg__IrSourceInfo__Sequence * member =
    (wiimote_msgs__msg__IrSourceInfo__Sequence *)(untyped_member);
  wiimote_msgs__msg__IrSourceInfo__Sequence__fini(member);
  return wiimote_msgs__msg__IrSourceInfo__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[20] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "angular_velocity_zeroed",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, angular_velocity_zeroed),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "angular_velocity_raw",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, angular_velocity_raw),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "angular_velocity_covariance",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    9,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, angular_velocity_covariance),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__angular_velocity_covariance,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__angular_velocity_covariance,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__angular_velocity_covariance,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__angular_velocity_covariance,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__angular_velocity_covariance,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "linear_acceleration_zeroed",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, linear_acceleration_zeroed),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "linear_acceleration_raw",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, linear_acceleration_raw),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "linear_acceleration_covariance",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    9,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, linear_acceleration_covariance),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__linear_acceleration_covariance,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__linear_acceleration_covariance,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__linear_acceleration_covariance,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__linear_acceleration_covariance,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__linear_acceleration_covariance,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "nunchuk_acceleration_zeroed",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, nunchuk_acceleration_zeroed),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "nunchuk_acceleration_raw",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, nunchuk_acceleration_raw),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "nunchuk_joystick_zeroed",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    2,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, nunchuk_joystick_zeroed),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__nunchuk_joystick_zeroed,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_joystick_zeroed,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_joystick_zeroed,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__nunchuk_joystick_zeroed,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__nunchuk_joystick_zeroed,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "nunchuk_joystick_raw",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    2,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, nunchuk_joystick_raw),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__nunchuk_joystick_raw,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_joystick_raw,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_joystick_raw,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__nunchuk_joystick_raw,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__nunchuk_joystick_raw,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "buttons",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    11,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, buttons),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__buttons,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__buttons,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__buttons,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__buttons,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__buttons,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "nunchuk_buttons",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    2,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, nunchuk_buttons),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__nunchuk_buttons,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__nunchuk_buttons,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__nunchuk_buttons,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__nunchuk_buttons,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__nunchuk_buttons,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "leds",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    4,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, leds),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__leds,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__leds,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__leds,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__leds,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__leds,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "rumble",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, rumble),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "ir_tracking",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, ir_tracking),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__size_function__State__ir_tracking,  // size() function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_const_function__State__ir_tracking,  // get_const(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__get_function__State__ir_tracking,  // get(index) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__fetch_function__State__ir_tracking,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__assign_function__State__ir_tracking,  // assign(index, value) function pointer
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__resize_function__State__ir_tracking  // resize(index) function pointer
  },
  {
    "raw_battery",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, raw_battery),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "percent_battery",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, percent_battery),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "zeroing_time",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, zeroing_time),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "errors",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT64,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__State, errors),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_members = {
  "wiimote_msgs__msg",  // message namespace
  "State",  // message name
  20,  // number of fields
  sizeof(wiimote_msgs__msg__State),
  false,  // has_any_key_member_
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array,  // message members
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_init_function,  // function to initialize message memory (memory has to be allocated)
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle = {
  0,
  &wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_members,
  get_message_typesupport_handle_function,
  &wiimote_msgs__msg__State__get_type_hash,
  &wiimote_msgs__msg__State__get_type_description,
  &wiimote_msgs__msg__State__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_wiimote_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, wiimote_msgs, msg, State)() {
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[4].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[5].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[7].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[8].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[15].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, wiimote_msgs, msg, IrSourceInfo)();
  wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_member_array[18].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle.typesupport_identifier) {
    wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &wiimote_msgs__msg__State__rosidl_typesupport_introspection_c__State_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
