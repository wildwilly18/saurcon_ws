// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/ir_source_info.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__BUILDER_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "wiimote_msgs/msg/detail/ir_source_info__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace wiimote_msgs
{

namespace msg
{

namespace builder
{

class Init_IrSourceInfo_ir_size
{
public:
  explicit Init_IrSourceInfo_ir_size(::wiimote_msgs::msg::IrSourceInfo & msg)
  : msg_(msg)
  {}
  ::wiimote_msgs::msg::IrSourceInfo ir_size(::wiimote_msgs::msg::IrSourceInfo::_ir_size_type arg)
  {
    msg_.ir_size = std::move(arg);
    return std::move(msg_);
  }

private:
  ::wiimote_msgs::msg::IrSourceInfo msg_;
};

class Init_IrSourceInfo_y
{
public:
  explicit Init_IrSourceInfo_y(::wiimote_msgs::msg::IrSourceInfo & msg)
  : msg_(msg)
  {}
  Init_IrSourceInfo_ir_size y(::wiimote_msgs::msg::IrSourceInfo::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_IrSourceInfo_ir_size(msg_);
  }

private:
  ::wiimote_msgs::msg::IrSourceInfo msg_;
};

class Init_IrSourceInfo_x
{
public:
  Init_IrSourceInfo_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_IrSourceInfo_y x(::wiimote_msgs::msg::IrSourceInfo::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_IrSourceInfo_y(msg_);
  }

private:
  ::wiimote_msgs::msg::IrSourceInfo msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::wiimote_msgs::msg::IrSourceInfo>()
{
  return wiimote_msgs::msg::builder::Init_IrSourceInfo_x();
}

}  // namespace wiimote_msgs

#endif  // WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__BUILDER_HPP_
