// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "wiimote_msgs/msg/detail/timed_switch__rosidl_typesupport_introspection_c.h"
#include "wiimote_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "wiimote_msgs/msg/detail/timed_switch__functions.h"
#include "wiimote_msgs/msg/detail/timed_switch__struct.h"


// Include directives for member types
// Member `pulse_pattern`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  wiimote_msgs__msg__TimedSwitch__init(message_memory);
}

void wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_fini_function(void * message_memory)
{
  wiimote_msgs__msg__TimedSwitch__fini(message_memory);
}

size_t wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__size_function__TimedSwitch__pulse_pattern(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__get_const_function__TimedSwitch__pulse_pattern(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__get_function__TimedSwitch__pulse_pattern(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__fetch_function__TimedSwitch__pulse_pattern(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__get_const_function__TimedSwitch__pulse_pattern(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__assign_function__TimedSwitch__pulse_pattern(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__get_function__TimedSwitch__pulse_pattern(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__resize_function__TimedSwitch__pulse_pattern(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_member_array[3] = {
  {
    "switch_mode",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__TimedSwitch, switch_mode),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "num_cycles",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__TimedSwitch, num_cycles),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pulse_pattern",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__TimedSwitch, pulse_pattern),  // bytes offset in struct
    NULL,  // default value
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__size_function__TimedSwitch__pulse_pattern,  // size() function pointer
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__get_const_function__TimedSwitch__pulse_pattern,  // get_const(index) function pointer
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__get_function__TimedSwitch__pulse_pattern,  // get(index) function pointer
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__fetch_function__TimedSwitch__pulse_pattern,  // fetch(index, &value) function pointer
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__assign_function__TimedSwitch__pulse_pattern,  // assign(index, value) function pointer
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__resize_function__TimedSwitch__pulse_pattern  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_members = {
  "wiimote_msgs__msg",  // message namespace
  "TimedSwitch",  // message name
  3,  // number of fields
  sizeof(wiimote_msgs__msg__TimedSwitch),
  false,  // has_any_key_member_
  wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_member_array,  // message members
  wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_init_function,  // function to initialize message memory (memory has to be allocated)
  wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_type_support_handle = {
  0,
  &wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_members,
  get_message_typesupport_handle_function,
  &wiimote_msgs__msg__TimedSwitch__get_type_hash,
  &wiimote_msgs__msg__TimedSwitch__get_type_description,
  &wiimote_msgs__msg__TimedSwitch__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_wiimote_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, wiimote_msgs, msg, TimedSwitch)() {
  if (!wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_type_support_handle.typesupport_identifier) {
    wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &wiimote_msgs__msg__TimedSwitch__rosidl_typesupport_introspection_c__TimedSwitch_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
