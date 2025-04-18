// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "wiimote_msgs/msg/detail/ir_source_info__rosidl_typesupport_introspection_c.h"
#include "wiimote_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "wiimote_msgs/msg/detail/ir_source_info__functions.h"
#include "wiimote_msgs/msg/detail/ir_source_info__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  wiimote_msgs__msg__IrSourceInfo__init(message_memory);
}

void wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_fini_function(void * message_memory)
{
  wiimote_msgs__msg__IrSourceInfo__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_member_array[3] = {
  {
    "x",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__IrSourceInfo, x),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "y",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__IrSourceInfo, y),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "ir_size",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT64,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs__msg__IrSourceInfo, ir_size),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_members = {
  "wiimote_msgs__msg",  // message namespace
  "IrSourceInfo",  // message name
  3,  // number of fields
  sizeof(wiimote_msgs__msg__IrSourceInfo),
  false,  // has_any_key_member_
  wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_member_array,  // message members
  wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_init_function,  // function to initialize message memory (memory has to be allocated)
  wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_type_support_handle = {
  0,
  &wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_members,
  get_message_typesupport_handle_function,
  &wiimote_msgs__msg__IrSourceInfo__get_type_hash,
  &wiimote_msgs__msg__IrSourceInfo__get_type_description,
  &wiimote_msgs__msg__IrSourceInfo__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_wiimote_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, wiimote_msgs, msg, IrSourceInfo)() {
  if (!wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_type_support_handle.typesupport_identifier) {
    wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &wiimote_msgs__msg__IrSourceInfo__rosidl_typesupport_introspection_c__IrSourceInfo_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
