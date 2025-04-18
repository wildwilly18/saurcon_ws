// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/timed_switch.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__STRUCT_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__wiimote_msgs__msg__TimedSwitch __attribute__((deprecated))
#else
# define DEPRECATED__wiimote_msgs__msg__TimedSwitch __declspec(deprecated)
#endif

namespace wiimote_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TimedSwitch_
{
  using Type = TimedSwitch_<ContainerAllocator>;

  explicit TimedSwitch_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->switch_mode = 0;
      this->num_cycles = 0l;
    }
  }

  explicit TimedSwitch_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->switch_mode = 0;
      this->num_cycles = 0l;
    }
  }

  // field types and members
  using _switch_mode_type =
    int8_t;
  _switch_mode_type switch_mode;
  using _num_cycles_type =
    int32_t;
  _num_cycles_type num_cycles;
  using _pulse_pattern_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _pulse_pattern_type pulse_pattern;

  // setters for named parameter idiom
  Type & set__switch_mode(
    const int8_t & _arg)
  {
    this->switch_mode = _arg;
    return *this;
  }
  Type & set__num_cycles(
    const int32_t & _arg)
  {
    this->num_cycles = _arg;
    return *this;
  }
  Type & set__pulse_pattern(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->pulse_pattern = _arg;
    return *this;
  }

  // constant declarations
  static constexpr int8_t ON =
    1;
  static constexpr int8_t OFF =
    0;
  static constexpr int8_t NO_CHANGE =
    -2;
  static constexpr int8_t REPEAT =
    -1;
  static constexpr int8_t FOREVER =
    -1;

  // pointer types
  using RawPtr =
    wiimote_msgs::msg::TimedSwitch_<ContainerAllocator> *;
  using ConstRawPtr =
    const wiimote_msgs::msg::TimedSwitch_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wiimote_msgs::msg::TimedSwitch_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wiimote_msgs::msg::TimedSwitch_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wiimote_msgs__msg__TimedSwitch
    std::shared_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wiimote_msgs__msg__TimedSwitch
    std::shared_ptr<wiimote_msgs::msg::TimedSwitch_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TimedSwitch_ & other) const
  {
    if (this->switch_mode != other.switch_mode) {
      return false;
    }
    if (this->num_cycles != other.num_cycles) {
      return false;
    }
    if (this->pulse_pattern != other.pulse_pattern) {
      return false;
    }
    return true;
  }
  bool operator!=(const TimedSwitch_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TimedSwitch_

// alias to use template instance with default allocator
using TimedSwitch =
  wiimote_msgs::msg::TimedSwitch_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t TimedSwitch_<ContainerAllocator>::ON;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t TimedSwitch_<ContainerAllocator>::OFF;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t TimedSwitch_<ContainerAllocator>::NO_CHANGE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t TimedSwitch_<ContainerAllocator>::REPEAT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t TimedSwitch_<ContainerAllocator>::FOREVER;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace wiimote_msgs

#endif  // WIIMOTE_MSGS__MSG__DETAIL__TIMED_SWITCH__STRUCT_HPP_
