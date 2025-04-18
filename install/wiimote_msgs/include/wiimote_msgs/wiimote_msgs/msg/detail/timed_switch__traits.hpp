// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/timed_switch.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__TRAITS_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "wiimote_msgs/msg/detail/timed_switch__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace wiimote_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TimedSwitch & msg,
  std::ostream & out)
{
  out << "{";
  // member: switch_mode
  {
    out << "switch_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.switch_mode, out);
    out << ", ";
  }

  // member: num_cycles
  {
    out << "num_cycles: ";
    rosidl_generator_traits::value_to_yaml(msg.num_cycles, out);
    out << ", ";
  }

  // member: pulse_pattern
  {
    if (msg.pulse_pattern.size() == 0) {
      out << "pulse_pattern: []";
    } else {
      out << "pulse_pattern: [";
      size_t pending_items = msg.pulse_pattern.size();
      for (auto item : msg.pulse_pattern) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TimedSwitch & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: switch_mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "switch_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.switch_mode, out);
    out << "\n";
  }

  // member: num_cycles
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "num_cycles: ";
    rosidl_generator_traits::value_to_yaml(msg.num_cycles, out);
    out << "\n";
  }

  // member: pulse_pattern
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.pulse_pattern.size() == 0) {
      out << "pulse_pattern: []\n";
    } else {
      out << "pulse_pattern:\n";
      for (auto item : msg.pulse_pattern) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TimedSwitch & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace wiimote_msgs

namespace rosidl_generator_traits
{

[[deprecated("use wiimote_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const wiimote_msgs::msg::TimedSwitch & msg,
  std::ostream & out, size_t indentation = 0)
{
  wiimote_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use wiimote_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const wiimote_msgs::msg::TimedSwitch & msg)
{
  return wiimote_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<wiimote_msgs::msg::TimedSwitch>()
{
  return "wiimote_msgs::msg::TimedSwitch";
}

template<>
inline const char * name<wiimote_msgs::msg::TimedSwitch>()
{
  return "wiimote_msgs/msg/TimedSwitch";
}

template<>
struct has_fixed_size<wiimote_msgs::msg::TimedSwitch>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<wiimote_msgs::msg::TimedSwitch>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<wiimote_msgs::msg::TimedSwitch>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__TRAITS_HPP_
