// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/timed_switch.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__BUILDER_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wiimote_msgs/msg/detail/timed_switch__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wiimote_msgs
{

namespace msg
{

namespace builder
{

class Init_TimedSwitch_pulse_pattern
{
public:
  explicit Init_TimedSwitch_pulse_pattern(::wiimote_msgs::msg::TimedSwitch & msg)
  : msg_(msg)
  {}
  ::wiimote_msgs::msg::TimedSwitch pulse_pattern(::wiimote_msgs::msg::TimedSwitch::_pulse_pattern_type arg)
  {
    msg_.pulse_pattern = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wiimote_msgs::msg::TimedSwitch msg_;
};

class Init_TimedSwitch_num_cycles
{
public:
  explicit Init_TimedSwitch_num_cycles(::wiimote_msgs::msg::TimedSwitch & msg)
  : msg_(msg)
  {}
  Init_TimedSwitch_pulse_pattern num_cycles(::wiimote_msgs::msg::TimedSwitch::_num_cycles_type arg)
  {
    msg_.num_cycles = std::move(arg);
    return Init_TimedSwitch_pulse_pattern(msg_);
  }

private:
  ::wiimote_msgs::msg::TimedSwitch msg_;
};

class Init_TimedSwitch_switch_mode
{
public:
  Init_TimedSwitch_switch_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TimedSwitch_num_cycles switch_mode(::wiimote_msgs::msg::TimedSwitch::_switch_mode_type arg)
  {
    msg_.switch_mode = std::move(arg);
    return Init_TimedSwitch_num_cycles(msg_);
  }

private:
  ::wiimote_msgs::msg::TimedSwitch msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wiimote_msgs::msg::TimedSwitch>()
{
  return wiimote_msgs::msg::builder::Init_TimedSwitch_switch_mode();
}

}  // namespace wiimote_msgs

#endif  // WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__BUILDER_HPP_
