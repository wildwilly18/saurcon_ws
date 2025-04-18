// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "wiimote_msgs/msg/detail/state__functions.h"
#include "wiimote_msgs/msg/detail/state__struct.hpp"
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

void State_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) wiimote_msgs::msg::State(_init);
}

void State_fini_function(void * message_memory)
{
  auto typed_message = static_cast<wiimote_msgs::msg::State *>(message_memory);
  typed_message->~State();
}

size_t size_function__State__angular_velocity_covariance(const void * untyped_member)
{
  (void)untyped_member;
  return 9;
}

const void * get_const_function__State__angular_velocity_covariance(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<double, 9> *>(untyped_member);
  return &member[index];
}

void * get_function__State__angular_velocity_covariance(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<double, 9> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__angular_velocity_covariance(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const double *>(
    get_const_function__State__angular_velocity_covariance(untyped_member, index));
  auto & value = *reinterpret_cast<double *>(untyped_value);
  value = item;
}

void assign_function__State__angular_velocity_covariance(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<double *>(
    get_function__State__angular_velocity_covariance(untyped_member, index));
  const auto & value = *reinterpret_cast<const double *>(untyped_value);
  item = value;
}

size_t size_function__State__linear_acceleration_covariance(const void * untyped_member)
{
  (void)untyped_member;
  return 9;
}

const void * get_const_function__State__linear_acceleration_covariance(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<double, 9> *>(untyped_member);
  return &member[index];
}

void * get_function__State__linear_acceleration_covariance(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<double, 9> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__linear_acceleration_covariance(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const double *>(
    get_const_function__State__linear_acceleration_covariance(untyped_member, index));
  auto & value = *reinterpret_cast<double *>(untyped_value);
  value = item;
}

void assign_function__State__linear_acceleration_covariance(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<double *>(
    get_function__State__linear_acceleration_covariance(untyped_member, index));
  const auto & value = *reinterpret_cast<const double *>(untyped_value);
  item = value;
}

size_t size_function__State__nunchuk_joystick_zeroed(const void * untyped_member)
{
  (void)untyped_member;
  return 2;
}

const void * get_const_function__State__nunchuk_joystick_zeroed(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<float, 2> *>(untyped_member);
  return &member[index];
}

void * get_function__State__nunchuk_joystick_zeroed(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<float, 2> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__nunchuk_joystick_zeroed(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__State__nunchuk_joystick_zeroed(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__State__nunchuk_joystick_zeroed(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__State__nunchuk_joystick_zeroed(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

size_t size_function__State__nunchuk_joystick_raw(const void * untyped_member)
{
  (void)untyped_member;
  return 2;
}

const void * get_const_function__State__nunchuk_joystick_raw(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<float, 2> *>(untyped_member);
  return &member[index];
}

void * get_function__State__nunchuk_joystick_raw(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<float, 2> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__nunchuk_joystick_raw(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__State__nunchuk_joystick_raw(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__State__nunchuk_joystick_raw(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__State__nunchuk_joystick_raw(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

size_t size_function__State__buttons(const void * untyped_member)
{
  (void)untyped_member;
  return 11;
}

const void * get_const_function__State__buttons(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<bool, 11> *>(untyped_member);
  return &member[index];
}

void * get_function__State__buttons(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<bool, 11> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__buttons(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const bool *>(
    get_const_function__State__buttons(untyped_member, index));
  auto & value = *reinterpret_cast<bool *>(untyped_value);
  value = item;
}

void assign_function__State__buttons(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<bool *>(
    get_function__State__buttons(untyped_member, index));
  const auto & value = *reinterpret_cast<const bool *>(untyped_value);
  item = value;
}

size_t size_function__State__nunchuk_buttons(const void * untyped_member)
{
  (void)untyped_member;
  return 2;
}

const void * get_const_function__State__nunchuk_buttons(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<bool, 2> *>(untyped_member);
  return &member[index];
}

void * get_function__State__nunchuk_buttons(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<bool, 2> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__nunchuk_buttons(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const bool *>(
    get_const_function__State__nunchuk_buttons(untyped_member, index));
  auto & value = *reinterpret_cast<bool *>(untyped_value);
  value = item;
}

void assign_function__State__nunchuk_buttons(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<bool *>(
    get_function__State__nunchuk_buttons(untyped_member, index));
  const auto & value = *reinterpret_cast<const bool *>(untyped_value);
  item = value;
}

size_t size_function__State__leds(const void * untyped_member)
{
  (void)untyped_member;
  return 4;
}

const void * get_const_function__State__leds(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::array<bool, 4> *>(untyped_member);
  return &member[index];
}

void * get_function__State__leds(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::array<bool, 4> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__leds(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const bool *>(
    get_const_function__State__leds(untyped_member, index));
  auto & value = *reinterpret_cast<bool *>(untyped_value);
  value = item;
}

void assign_function__State__leds(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<bool *>(
    get_function__State__leds(untyped_member, index));
  const auto & value = *reinterpret_cast<const bool *>(untyped_value);
  item = value;
}

size_t size_function__State__ir_tracking(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<wiimote_msgs::msg::IrSourceInfo> *>(untyped_member);
  return member->size();
}

const void * get_const_function__State__ir_tracking(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<wiimote_msgs::msg::IrSourceInfo> *>(untyped_member);
  return &member[index];
}

void * get_function__State__ir_tracking(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<wiimote_msgs::msg::IrSourceInfo> *>(untyped_member);
  return &member[index];
}

void fetch_function__State__ir_tracking(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const wiimote_msgs::msg::IrSourceInfo *>(
    get_const_function__State__ir_tracking(untyped_member, index));
  auto & value = *reinterpret_cast<wiimote_msgs::msg::IrSourceInfo *>(untyped_value);
  value = item;
}

void assign_function__State__ir_tracking(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<wiimote_msgs::msg::IrSourceInfo *>(
    get_function__State__ir_tracking(untyped_member, index));
  const auto & value = *reinterpret_cast<const wiimote_msgs::msg::IrSourceInfo *>(untyped_value);
  item = value;
}

void resize_function__State__ir_tracking(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<wiimote_msgs::msg::IrSourceInfo> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember State_message_member_array[20] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "angular_velocity_zeroed",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Vector3>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, angular_velocity_zeroed),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "angular_velocity_raw",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Vector3>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, angular_velocity_raw),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "angular_velocity_covariance",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    9,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, angular_velocity_covariance),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__angular_velocity_covariance,  // size() function pointer
    get_const_function__State__angular_velocity_covariance,  // get_const(index) function pointer
    get_function__State__angular_velocity_covariance,  // get(index) function pointer
    fetch_function__State__angular_velocity_covariance,  // fetch(index, &value) function pointer
    assign_function__State__angular_velocity_covariance,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "linear_acceleration_zeroed",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Vector3>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, linear_acceleration_zeroed),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "linear_acceleration_raw",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Vector3>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, linear_acceleration_raw),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "linear_acceleration_covariance",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    9,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, linear_acceleration_covariance),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__linear_acceleration_covariance,  // size() function pointer
    get_const_function__State__linear_acceleration_covariance,  // get_const(index) function pointer
    get_function__State__linear_acceleration_covariance,  // get(index) function pointer
    fetch_function__State__linear_acceleration_covariance,  // fetch(index, &value) function pointer
    assign_function__State__linear_acceleration_covariance,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "nunchuk_acceleration_zeroed",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Vector3>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, nunchuk_acceleration_zeroed),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "nunchuk_acceleration_raw",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Vector3>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, nunchuk_acceleration_raw),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "nunchuk_joystick_zeroed",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    2,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, nunchuk_joystick_zeroed),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__nunchuk_joystick_zeroed,  // size() function pointer
    get_const_function__State__nunchuk_joystick_zeroed,  // get_const(index) function pointer
    get_function__State__nunchuk_joystick_zeroed,  // get(index) function pointer
    fetch_function__State__nunchuk_joystick_zeroed,  // fetch(index, &value) function pointer
    assign_function__State__nunchuk_joystick_zeroed,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "nunchuk_joystick_raw",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    2,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, nunchuk_joystick_raw),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__nunchuk_joystick_raw,  // size() function pointer
    get_const_function__State__nunchuk_joystick_raw,  // get_const(index) function pointer
    get_function__State__nunchuk_joystick_raw,  // get(index) function pointer
    fetch_function__State__nunchuk_joystick_raw,  // fetch(index, &value) function pointer
    assign_function__State__nunchuk_joystick_raw,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "buttons",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    11,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, buttons),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__buttons,  // size() function pointer
    get_const_function__State__buttons,  // get_const(index) function pointer
    get_function__State__buttons,  // get(index) function pointer
    fetch_function__State__buttons,  // fetch(index, &value) function pointer
    assign_function__State__buttons,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "nunchuk_buttons",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    2,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, nunchuk_buttons),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__nunchuk_buttons,  // size() function pointer
    get_const_function__State__nunchuk_buttons,  // get_const(index) function pointer
    get_function__State__nunchuk_buttons,  // get(index) function pointer
    fetch_function__State__nunchuk_buttons,  // fetch(index, &value) function pointer
    assign_function__State__nunchuk_buttons,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "leds",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    4,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, leds),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__leds,  // size() function pointer
    get_const_function__State__leds,  // get_const(index) function pointer
    get_function__State__leds,  // get(index) function pointer
    fetch_function__State__leds,  // fetch(index, &value) function pointer
    assign_function__State__leds,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "rumble",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, rumble),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "ir_tracking",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<wiimote_msgs::msg::IrSourceInfo>(),  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, ir_tracking),  // bytes offset in struct
    nullptr,  // default value
    size_function__State__ir_tracking,  // size() function pointer
    get_const_function__State__ir_tracking,  // get_const(index) function pointer
    get_function__State__ir_tracking,  // get(index) function pointer
    fetch_function__State__ir_tracking,  // fetch(index, &value) function pointer
    assign_function__State__ir_tracking,  // assign(index, value) function pointer
    resize_function__State__ir_tracking  // resize(index) function pointer
  },
  {
    "raw_battery",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, raw_battery),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "percent_battery",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, percent_battery),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "zeroing_time",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<builtin_interfaces::msg::Time>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, zeroing_time),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "errors",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_UINT64,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(wiimote_msgs::msg::State, errors),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers State_message_members = {
  "wiimote_msgs::msg",  // message namespace
  "State",  // message name
  20,  // number of fields
  sizeof(wiimote_msgs::msg::State),
  false,  // has_any_key_member_
  State_message_member_array,  // message members
  State_init_function,  // function to initialize message memory (memory has to be allocated)
  State_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t State_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &State_message_members,
  get_message_typesupport_handle_function,
  &wiimote_msgs__msg__State__get_type_hash,
  &wiimote_msgs__msg__State__get_type_description,
  &wiimote_msgs__msg__State__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace wiimote_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<wiimote_msgs::msg::State>()
{
  return &::wiimote_msgs::msg::rosidl_typesupport_introspection_cpp::State_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, wiimote_msgs, msg, State)() {
  return &::wiimote_msgs::msg::rosidl_typesupport_introspection_cpp::State_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
