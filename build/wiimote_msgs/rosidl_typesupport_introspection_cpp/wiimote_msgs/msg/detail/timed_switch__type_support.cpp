// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "wiimote_msgs/msg/detail/timed_switch__functions.h"
#include "wiimote_msgs/msg/detail/timed_switch__struct.hpp"
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

void TimedSwitch_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) wiimote_msgs::msg::TimedSwitch(_init);
}

void TimedSwitch_fini_function(void * message_memory)
{
  auto typed_message = static_cast<wiimote_msgs::msg::TimedSwitch *>(message_memory);
  typed_message->~TimedSwitch();
}

size_t size_function__TimedSwitch__pulse_pattern(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<float> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TimedSwitch__pulse_pattern(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<float> *>(untyped_member);
  return &member[index];
}

void * get_function__TimedSwitch__pulse_pattern(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<float> *>(untyped_member);
  return &member[index];
}

void fetch_function__TimedSwitch__pulse_pattern(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__TimedSwitch__pulse_pattern(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__TimedSwitch__pulse_pattern(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__TimedSwitch__pulse_pattern(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

void resize_function__TimedSwitch__pulse_pattern(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<float> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember TimedSwitch_message_member_array[3] = {
  {
    "switch_mode",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::TimedSwitch, switch_mode),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "num_cycles",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::TimedSwitch, num_cycles),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "pulse_pattern",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::TimedSwitch, pulse_pattern),  // bytes offset in struct
    nullptr,  // default value
    size_function__TimedSwitch__pulse_pattern,  // size() function pointer
    get_const_function__TimedSwitch__pulse_pattern,  // get_const(index) function pointer
    get_function__TimedSwitch__pulse_pattern,  // get(index) function pointer
    fetch_function__TimedSwitch__pulse_pattern,  // fetch(index, &value) function pointer
    assign_function__TimedSwitch__pulse_pattern,  // assign(index, value) function pointer
    resize_function__TimedSwitch__pulse_pattern  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers TimedSwitch_message_members = {
  "wiimote_msgs::msg",  // message namespace
  "TimedSwitch",  // message name
  3,  // number of fields
  sizeof(wiimote_msgs::msg::TimedSwitch),
  false,  // has_any_key_member_
  TimedSwitch_message_member_array,  // message members
  TimedSwitch_init_function,  // function to initialize message memory (memory has to be allocated)
  TimedSwitch_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t TimedSwitch_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &TimedSwitch_message_members,
  get_message_typesupport_handle_function,
  &wiimote_msgs__msg__TimedSwitch__get_type_hash,
  &wiimote_msgs__msg__TimedSwitch__get_type_description,
  &wiimote_msgs__msg__TimedSwitch__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace wiimote_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<wiimote_msgs::msg::TimedSwitch>()
{
  return &::wiimote_msgs::msg::rosidl_typesupport_introspection_cpp::TimedSwitch_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, wiimote_msgs, msg, TimedSwitch)() {
  return &::wiimote_msgs::msg::rosidl_typesupport_introspection_cpp::TimedSwitch_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
