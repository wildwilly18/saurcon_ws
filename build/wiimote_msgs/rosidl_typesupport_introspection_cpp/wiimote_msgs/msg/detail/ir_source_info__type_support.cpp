// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "wiimote_msgs/msg/detail/ir_source_info__functions.h"
#include "wiimote_msgs/msg/detail/ir_source_info__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace wiimote_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void IrSourceInfo_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) wiimote_msgs::msg::IrSourceInfo(_init);
}

void IrSourceInfo_fini_function(void * message_memory)
{
  auto typed_message = static_cast<wiimote_msgs::msg::IrSourceInfo *>(message_memory);
  typed_message->~IrSourceInfo();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember IrSourceInfo_message_member_array[3] = {
  {
    "x",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::IrSourceInfo, x),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "y",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::IrSourceInfo, y),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "ir_size",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT64,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::IrSourceInfo, ir_size),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers IrSourceInfo_message_members = {
  "wiimote_msgs::msg",  // message namespace
  "IrSourceInfo",  // message name
  3,  // number of fields
  sizeof(wiimote_msgs::msg::IrSourceInfo),
  false,  // has_any_key_member_
  IrSourceInfo_message_member_array,  // message members
  IrSourceInfo_init_function,  // function to initialize message memory (memory has to be allocated)
  IrSourceInfo_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t IrSourceInfo_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &IrSourceInfo_message_members,
  get_message_typesupport_handle_function,
  &wiimote_msgs__msg__IrSourceInfo__get_type_hash,
  &wiimote_msgs__msg__IrSourceInfo__get_type_description,
  &wiimote_msgs__msg__IrSourceInfo__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace wiimote_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<wiimote_msgs::msg::IrSourceInfo>()
{
  return &::wiimote_msgs::msg::rosidl_typesupport_introspection_cpp::IrSourceInfo_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, wiimote_msgs, msg, IrSourceInfo)() {
  return &::wiimote_msgs::msg::rosidl_typesupport_introspection_cpp::IrSourceInfo_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
