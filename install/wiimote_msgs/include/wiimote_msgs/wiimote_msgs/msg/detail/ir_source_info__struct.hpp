// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/ir_source_info.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__STRUCT_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__wiimote_msgs__msg__IrSourceInfo __attribute__((deprecated))
#else
# define DEPRECATED__wiimote_msgs__msg__IrSourceInfo __declspec(deprecated)
#endif

namespace wiimote_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct IrSourceInfo_
{
  using Type = IrSourceInfo_<ContainerAllocator>;

  explicit IrSourceInfo_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0;
      this->y = 0.0;
      this->ir_size = 0ll;
    }
  }

  explicit IrSourceInfo_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->x = 0.0;
      this->y = 0.0;
      this->ir_size = 0ll;
    }
  }

  // field types and members
  using _x_type =
    double;
  _x_type x;
  using _y_type =
    double;
  _y_type y;
  using _ir_size_type =
    int64_t;
  _ir_size_type ir_size;

  // setters for named parameter idiom
  Type & set__x(
    const double & _arg)
  {
    this->x = _arg;
    return *this;
  }
  Type & set__y(
    const double & _arg)
  {
    this->y = _arg;
    return *this;
  }
  Type & set__ir_size(
    const int64_t & _arg)
  {
    this->ir_size = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator> *;
  using ConstRawPtr =
    const wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wiimote_msgs__msg__IrSourceInfo
    std::shared_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wiimote_msgs__msg__IrSourceInfo
    std::shared_ptr<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const IrSourceInfo_ & other) const
  {
    if (this->x != other.x) {
      return false;
    }
    if (this->y != other.y) {
      return false;
    }
    if (this->ir_size != other.ir_size) {
      return false;
    }
    return true;
  }
  bool operator!=(const IrSourceInfo_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct IrSourceInfo_

// alias to use template instance with default allocator
using IrSourceInfo =
  wiimote_msgs::msg::IrSourceInfo_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace wiimote_msgs

#endif  // WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__STRUCT_HPP_
