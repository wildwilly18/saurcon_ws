// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/ir_source_info.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__TRAITS_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "wiimote_msgs/msg/detail/ir_source_info__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace wiimote_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const IrSourceInfo & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: ir_size
  {
    out << "ir_size: ";
    rosidl_generator_traits::value_to_yaml(msg.ir_size, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const IrSourceInfo & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: ir_size
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ir_size: ";
    rosidl_generator_traits::value_to_yaml(msg.ir_size, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const IrSourceInfo & msg, bool use_flow_style = false)
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
  const wiimote_msgs::msg::IrSourceInfo & msg,
  std::ostream & out, size_t indentation = 0)
{
  wiimote_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use wiimote_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const wiimote_msgs::msg::IrSourceInfo & msg)
{
  return wiimote_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<wiimote_msgs::msg::IrSourceInfo>()
{
  return "wiimote_msgs::msg::IrSourceInfo";
}

template<>
inline const char * name<wiimote_msgs::msg::IrSourceInfo>()
{
  return "wiimote_msgs/msg/IrSourceInfo";
}

template<>
struct has_fixed_size<wiimote_msgs::msg::IrSourceInfo>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<wiimote_msgs::msg::IrSourceInfo>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<wiimote_msgs::msg::IrSourceInfo>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__TRAITS_HPP_
