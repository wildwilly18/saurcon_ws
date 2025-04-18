// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/state.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__STATE__TRAITS_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__STATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "wiimote_msgs/msg/detail/state__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'angular_velocity_zeroed'
// Member 'angular_velocity_raw'
// Member 'linear_acceleration_zeroed'
// Member 'linear_acceleration_raw'
// Member 'nunchuk_acceleration_zeroed'
// Member 'nunchuk_acceleration_raw'
#include "geometry_msgs/msg/detail/vector3__traits.hpp"
// Member 'ir_tracking'
#include "wiimote_msgs/msg/detail/ir_source_info__traits.hpp"
// Member 'zeroing_time'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace wiimote_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const State & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: angular_velocity_zeroed
  {
    out << "angular_velocity_zeroed: ";
    to_flow_style_yaml(msg.angular_velocity_zeroed, out);
    out << ", ";
  }

  // member: angular_velocity_raw
  {
    out << "angular_velocity_raw: ";
    to_flow_style_yaml(msg.angular_velocity_raw, out);
    out << ", ";
  }

  // member: angular_velocity_covariance
  {
    if (msg.angular_velocity_covariance.size() == 0) {
      out << "angular_velocity_covariance: []";
    } else {
      out << "angular_velocity_covariance: [";
      size_t pending_items = msg.angular_velocity_covariance.size();
      for (auto item : msg.angular_velocity_covariance) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: linear_acceleration_zeroed
  {
    out << "linear_acceleration_zeroed: ";
    to_flow_style_yaml(msg.linear_acceleration_zeroed, out);
    out << ", ";
  }

  // member: linear_acceleration_raw
  {
    out << "linear_acceleration_raw: ";
    to_flow_style_yaml(msg.linear_acceleration_raw, out);
    out << ", ";
  }

  // member: linear_acceleration_covariance
  {
    if (msg.linear_acceleration_covariance.size() == 0) {
      out << "linear_acceleration_covariance: []";
    } else {
      out << "linear_acceleration_covariance: [";
      size_t pending_items = msg.linear_acceleration_covariance.size();
      for (auto item : msg.linear_acceleration_covariance) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: nunchuk_acceleration_zeroed
  {
    out << "nunchuk_acceleration_zeroed: ";
    to_flow_style_yaml(msg.nunchuk_acceleration_zeroed, out);
    out << ", ";
  }

  // member: nunchuk_acceleration_raw
  {
    out << "nunchuk_acceleration_raw: ";
    to_flow_style_yaml(msg.nunchuk_acceleration_raw, out);
    out << ", ";
  }

  // member: nunchuk_joystick_zeroed
  {
    if (msg.nunchuk_joystick_zeroed.size() == 0) {
      out << "nunchuk_joystick_zeroed: []";
    } else {
      out << "nunchuk_joystick_zeroed: [";
      size_t pending_items = msg.nunchuk_joystick_zeroed.size();
      for (auto item : msg.nunchuk_joystick_zeroed) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: nunchuk_joystick_raw
  {
    if (msg.nunchuk_joystick_raw.size() == 0) {
      out << "nunchuk_joystick_raw: []";
    } else {
      out << "nunchuk_joystick_raw: [";
      size_t pending_items = msg.nunchuk_joystick_raw.size();
      for (auto item : msg.nunchuk_joystick_raw) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: buttons
  {
    if (msg.buttons.size() == 0) {
      out << "buttons: []";
    } else {
      out << "buttons: [";
      size_t pending_items = msg.buttons.size();
      for (auto item : msg.buttons) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: nunchuk_buttons
  {
    if (msg.nunchuk_buttons.size() == 0) {
      out << "nunchuk_buttons: []";
    } else {
      out << "nunchuk_buttons: [";
      size_t pending_items = msg.nunchuk_buttons.size();
      for (auto item : msg.nunchuk_buttons) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: leds
  {
    if (msg.leds.size() == 0) {
      out << "leds: []";
    } else {
      out << "leds: [";
      size_t pending_items = msg.leds.size();
      for (auto item : msg.leds) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: rumble
  {
    out << "rumble: ";
    rosidl_generator_traits::value_to_yaml(msg.rumble, out);
    out << ", ";
  }

  // member: ir_tracking
  {
    if (msg.ir_tracking.size() == 0) {
      out << "ir_tracking: []";
    } else {
      out << "ir_tracking: [";
      size_t pending_items = msg.ir_tracking.size();
      for (auto item : msg.ir_tracking) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: raw_battery
  {
    out << "raw_battery: ";
    rosidl_generator_traits::value_to_yaml(msg.raw_battery, out);
    out << ", ";
  }

  // member: percent_battery
  {
    out << "percent_battery: ";
    rosidl_generator_traits::value_to_yaml(msg.percent_battery, out);
    out << ", ";
  }

  // member: zeroing_time
  {
    out << "zeroing_time: ";
    to_flow_style_yaml(msg.zeroing_time, out);
    out << ", ";
  }

  // member: errors
  {
    out << "errors: ";
    rosidl_generator_traits::value_to_yaml(msg.errors, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const State & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: angular_velocity_zeroed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "angular_velocity_zeroed:\n";
    to_block_style_yaml(msg.angular_velocity_zeroed, out, indentation + 2);
  }

  // member: angular_velocity_raw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "angular_velocity_raw:\n";
    to_block_style_yaml(msg.angular_velocity_raw, out, indentation + 2);
  }

  // member: angular_velocity_covariance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.angular_velocity_covariance.size() == 0) {
      out << "angular_velocity_covariance: []\n";
    } else {
      out << "angular_velocity_covariance:\n";
      for (auto item : msg.angular_velocity_covariance) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: linear_acceleration_zeroed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "linear_acceleration_zeroed:\n";
    to_block_style_yaml(msg.linear_acceleration_zeroed, out, indentation + 2);
  }

  // member: linear_acceleration_raw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "linear_acceleration_raw:\n";
    to_block_style_yaml(msg.linear_acceleration_raw, out, indentation + 2);
  }

  // member: linear_acceleration_covariance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.linear_acceleration_covariance.size() == 0) {
      out << "linear_acceleration_covariance: []\n";
    } else {
      out << "linear_acceleration_covariance:\n";
      for (auto item : msg.linear_acceleration_covariance) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: nunchuk_acceleration_zeroed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "nunchuk_acceleration_zeroed:\n";
    to_block_style_yaml(msg.nunchuk_acceleration_zeroed, out, indentation + 2);
  }

  // member: nunchuk_acceleration_raw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "nunchuk_acceleration_raw:\n";
    to_block_style_yaml(msg.nunchuk_acceleration_raw, out, indentation + 2);
  }

  // member: nunchuk_joystick_zeroed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.nunchuk_joystick_zeroed.size() == 0) {
      out << "nunchuk_joystick_zeroed: []\n";
    } else {
      out << "nunchuk_joystick_zeroed:\n";
      for (auto item : msg.nunchuk_joystick_zeroed) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: nunchuk_joystick_raw
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.nunchuk_joystick_raw.size() == 0) {
      out << "nunchuk_joystick_raw: []\n";
    } else {
      out << "nunchuk_joystick_raw:\n";
      for (auto item : msg.nunchuk_joystick_raw) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: buttons
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.buttons.size() == 0) {
      out << "buttons: []\n";
    } else {
      out << "buttons:\n";
      for (auto item : msg.buttons) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: nunchuk_buttons
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.nunchuk_buttons.size() == 0) {
      out << "nunchuk_buttons: []\n";
    } else {
      out << "nunchuk_buttons:\n";
      for (auto item : msg.nunchuk_buttons) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: leds
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.leds.size() == 0) {
      out << "leds: []\n";
    } else {
      out << "leds:\n";
      for (auto item : msg.leds) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: rumble
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rumble: ";
    rosidl_generator_traits::value_to_yaml(msg.rumble, out);
    out << "\n";
  }

  // member: ir_tracking
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.ir_tracking.size() == 0) {
      out << "ir_tracking: []\n";
    } else {
      out << "ir_tracking:\n";
      for (auto item : msg.ir_tracking) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: raw_battery
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "raw_battery: ";
    rosidl_generator_traits::value_to_yaml(msg.raw_battery, out);
    out << "\n";
  }

  // member: percent_battery
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "percent_battery: ";
    rosidl_generator_traits::value_to_yaml(msg.percent_battery, out);
    out << "\n";
  }

  // member: zeroing_time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "zeroing_time:\n";
    to_block_style_yaml(msg.zeroing_time, out, indentation + 2);
  }

  // member: errors
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "errors: ";
    rosidl_generator_traits::value_to_yaml(msg.errors, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const State & msg, bool use_flow_style = false)
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
  const wiimote_msgs::msg::State & msg,
  std::ostream & out, size_t indentation = 0)
{
  wiimote_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use wiimote_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const wiimote_msgs::msg::State & msg)
{
  return wiimote_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<wiimote_msgs::msg::State>()
{
  return "wiimote_msgs::msg::State";
}

template<>
inline const char * name<wiimote_msgs::msg::State>()
{
  return "wiimote_msgs/msg/State";
}

template<>
struct has_fixed_size<wiimote_msgs::msg::State>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<wiimote_msgs::msg::State>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<wiimote_msgs::msg::State>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // WIIMOTE_MSGS__MSG__DETAIL__STATE__TRAITS_HPP_
