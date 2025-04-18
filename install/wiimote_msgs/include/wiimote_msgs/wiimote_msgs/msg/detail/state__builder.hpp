// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/state.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__STATE__BUILDER_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__STATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wiimote_msgs/msg/detail/state__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wiimote_msgs
{

namespace msg
{

namespace builder
{

class Init_State_errors
{
public:
  explicit Init_State_errors(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  ::wiimote_msgs::msg::State errors(::wiimote_msgs::msg::State::_errors_type arg)
  {
    msg_.errors = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_zeroing_time
{
public:
  explicit Init_State_zeroing_time(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_errors zeroing_time(::wiimote_msgs::msg::State::_zeroing_time_type arg)
  {
    msg_.zeroing_time = std::move(arg);
    return Init_State_errors(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_percent_battery
{
public:
  explicit Init_State_percent_battery(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_zeroing_time percent_battery(::wiimote_msgs::msg::State::_percent_battery_type arg)
  {
    msg_.percent_battery = std::move(arg);
    return Init_State_zeroing_time(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_raw_battery
{
public:
  explicit Init_State_raw_battery(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_percent_battery raw_battery(::wiimote_msgs::msg::State::_raw_battery_type arg)
  {
    msg_.raw_battery = std::move(arg);
    return Init_State_percent_battery(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_ir_tracking
{
public:
  explicit Init_State_ir_tracking(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_raw_battery ir_tracking(::wiimote_msgs::msg::State::_ir_tracking_type arg)
  {
    msg_.ir_tracking = std::move(arg);
    return Init_State_raw_battery(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_rumble
{
public:
  explicit Init_State_rumble(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_ir_tracking rumble(::wiimote_msgs::msg::State::_rumble_type arg)
  {
    msg_.rumble = std::move(arg);
    return Init_State_ir_tracking(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_leds
{
public:
  explicit Init_State_leds(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_rumble leds(::wiimote_msgs::msg::State::_leds_type arg)
  {
    msg_.leds = std::move(arg);
    return Init_State_rumble(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_nunchuk_buttons
{
public:
  explicit Init_State_nunchuk_buttons(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_leds nunchuk_buttons(::wiimote_msgs::msg::State::_nunchuk_buttons_type arg)
  {
    msg_.nunchuk_buttons = std::move(arg);
    return Init_State_leds(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_buttons
{
public:
  explicit Init_State_buttons(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_nunchuk_buttons buttons(::wiimote_msgs::msg::State::_buttons_type arg)
  {
    msg_.buttons = std::move(arg);
    return Init_State_nunchuk_buttons(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_nunchuk_joystick_raw
{
public:
  explicit Init_State_nunchuk_joystick_raw(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_buttons nunchuk_joystick_raw(::wiimote_msgs::msg::State::_nunchuk_joystick_raw_type arg)
  {
    msg_.nunchuk_joystick_raw = std::move(arg);
    return Init_State_buttons(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_nunchuk_joystick_zeroed
{
public:
  explicit Init_State_nunchuk_joystick_zeroed(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_nunchuk_joystick_raw nunchuk_joystick_zeroed(::wiimote_msgs::msg::State::_nunchuk_joystick_zeroed_type arg)
  {
    msg_.nunchuk_joystick_zeroed = std::move(arg);
    return Init_State_nunchuk_joystick_raw(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_nunchuk_acceleration_raw
{
public:
  explicit Init_State_nunchuk_acceleration_raw(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_nunchuk_joystick_zeroed nunchuk_acceleration_raw(::wiimote_msgs::msg::State::_nunchuk_acceleration_raw_type arg)
  {
    msg_.nunchuk_acceleration_raw = std::move(arg);
    return Init_State_nunchuk_joystick_zeroed(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_nunchuk_acceleration_zeroed
{
public:
  explicit Init_State_nunchuk_acceleration_zeroed(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_nunchuk_acceleration_raw nunchuk_acceleration_zeroed(::wiimote_msgs::msg::State::_nunchuk_acceleration_zeroed_type arg)
  {
    msg_.nunchuk_acceleration_zeroed = std::move(arg);
    return Init_State_nunchuk_acceleration_raw(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_linear_acceleration_covariance
{
public:
  explicit Init_State_linear_acceleration_covariance(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_nunchuk_acceleration_zeroed linear_acceleration_covariance(::wiimote_msgs::msg::State::_linear_acceleration_covariance_type arg)
  {
    msg_.linear_acceleration_covariance = std::move(arg);
    return Init_State_nunchuk_acceleration_zeroed(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_linear_acceleration_raw
{
public:
  explicit Init_State_linear_acceleration_raw(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_linear_acceleration_covariance linear_acceleration_raw(::wiimote_msgs::msg::State::_linear_acceleration_raw_type arg)
  {
    msg_.linear_acceleration_raw = std::move(arg);
    return Init_State_linear_acceleration_covariance(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_linear_acceleration_zeroed
{
public:
  explicit Init_State_linear_acceleration_zeroed(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_linear_acceleration_raw linear_acceleration_zeroed(::wiimote_msgs::msg::State::_linear_acceleration_zeroed_type arg)
  {
    msg_.linear_acceleration_zeroed = std::move(arg);
    return Init_State_linear_acceleration_raw(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_angular_velocity_covariance
{
public:
  explicit Init_State_angular_velocity_covariance(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_linear_acceleration_zeroed angular_velocity_covariance(::wiimote_msgs::msg::State::_angular_velocity_covariance_type arg)
  {
    msg_.angular_velocity_covariance = std::move(arg);
    return Init_State_linear_acceleration_zeroed(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_angular_velocity_raw
{
public:
  explicit Init_State_angular_velocity_raw(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_angular_velocity_covariance angular_velocity_raw(::wiimote_msgs::msg::State::_angular_velocity_raw_type arg)
  {
    msg_.angular_velocity_raw = std::move(arg);
    return Init_State_angular_velocity_covariance(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_angular_velocity_zeroed
{
public:
  explicit Init_State_angular_velocity_zeroed(::wiimote_msgs::msg::State & msg)
  : msg_(msg)
  {}
  Init_State_angular_velocity_raw angular_velocity_zeroed(::wiimote_msgs::msg::State::_angular_velocity_zeroed_type arg)
  {
    msg_.angular_velocity_zeroed = std::move(arg);
    return Init_State_angular_velocity_raw(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

class Init_State_header
{
public:
  Init_State_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_State_angular_velocity_zeroed header(::wiimote_msgs::msg::State::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_State_angular_velocity_zeroed(msg_);
  }

private:
  ::wiimote_msgs::msg::State msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wiimote_msgs::msg::State>()
{
  return wiimote_msgs::msg::builder::Init_State_header();
}

}  // namespace wiimote_msgs

#endif  // WIIMOTE_MSGS__MSG__DETAIL__STATE__BUILDER_HPP_
