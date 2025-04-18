// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/state.hpp"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__STATE__STRUCT_HPP_
#define WIIMOTE_MSGS__MSG__DETAIL__STATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'angular_velocity_zeroed'
// Member 'angular_velocity_raw'
// Member 'linear_acceleration_zeroed'
// Member 'linear_acceleration_raw'
// Member 'nunchuk_acceleration_zeroed'
// Member 'nunchuk_acceleration_raw'
#include "geometry_msgs/msg/detail/vector3__struct.hpp"
// Member 'ir_tracking'
#include "wiimote_msgs/msg/detail/ir_source_info__struct.hpp"
// Member 'zeroing_time'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__wiimote_msgs__msg__State __attribute__((deprecated))
#else
# define DEPRECATED__wiimote_msgs__msg__State __declspec(deprecated)
#endif

namespace wiimote_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct State_
{
  using Type = State_<ContainerAllocator>;

  explicit State_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    angular_velocity_zeroed(_init),
    angular_velocity_raw(_init),
    linear_acceleration_zeroed(_init),
    linear_acceleration_raw(_init),
    nunchuk_acceleration_zeroed(_init),
    nunchuk_acceleration_raw(_init),
    zeroing_time(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 9>::iterator, double>(this->angular_velocity_covariance.begin(), this->angular_velocity_covariance.end(), 0.0);
      std::fill<typename std::array<double, 9>::iterator, double>(this->linear_acceleration_covariance.begin(), this->linear_acceleration_covariance.end(), 0.0);
      std::fill<typename std::array<float, 2>::iterator, float>(this->nunchuk_joystick_zeroed.begin(), this->nunchuk_joystick_zeroed.end(), 0.0f);
      std::fill<typename std::array<float, 2>::iterator, float>(this->nunchuk_joystick_raw.begin(), this->nunchuk_joystick_raw.end(), 0.0f);
      std::fill<typename std::array<bool, 11>::iterator, bool>(this->buttons.begin(), this->buttons.end(), false);
      std::fill<typename std::array<bool, 2>::iterator, bool>(this->nunchuk_buttons.begin(), this->nunchuk_buttons.end(), false);
      std::fill<typename std::array<bool, 4>::iterator, bool>(this->leds.begin(), this->leds.end(), false);
      this->rumble = false;
      this->raw_battery = 0.0f;
      this->percent_battery = 0.0f;
      this->errors = 0ull;
    }
  }

  explicit State_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    angular_velocity_zeroed(_alloc, _init),
    angular_velocity_raw(_alloc, _init),
    angular_velocity_covariance(_alloc),
    linear_acceleration_zeroed(_alloc, _init),
    linear_acceleration_raw(_alloc, _init),
    linear_acceleration_covariance(_alloc),
    nunchuk_acceleration_zeroed(_alloc, _init),
    nunchuk_acceleration_raw(_alloc, _init),
    nunchuk_joystick_zeroed(_alloc),
    nunchuk_joystick_raw(_alloc),
    buttons(_alloc),
    nunchuk_buttons(_alloc),
    leds(_alloc),
    zeroing_time(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      std::fill<typename std::array<double, 9>::iterator, double>(this->angular_velocity_covariance.begin(), this->angular_velocity_covariance.end(), 0.0);
      std::fill<typename std::array<double, 9>::iterator, double>(this->linear_acceleration_covariance.begin(), this->linear_acceleration_covariance.end(), 0.0);
      std::fill<typename std::array<float, 2>::iterator, float>(this->nunchuk_joystick_zeroed.begin(), this->nunchuk_joystick_zeroed.end(), 0.0f);
      std::fill<typename std::array<float, 2>::iterator, float>(this->nunchuk_joystick_raw.begin(), this->nunchuk_joystick_raw.end(), 0.0f);
      std::fill<typename std::array<bool, 11>::iterator, bool>(this->buttons.begin(), this->buttons.end(), false);
      std::fill<typename std::array<bool, 2>::iterator, bool>(this->nunchuk_buttons.begin(), this->nunchuk_buttons.end(), false);
      std::fill<typename std::array<bool, 4>::iterator, bool>(this->leds.begin(), this->leds.end(), false);
      this->rumble = false;
      this->raw_battery = 0.0f;
      this->percent_battery = 0.0f;
      this->errors = 0ull;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _angular_velocity_zeroed_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _angular_velocity_zeroed_type angular_velocity_zeroed;
  using _angular_velocity_raw_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _angular_velocity_raw_type angular_velocity_raw;
  using _angular_velocity_covariance_type =
    std::array<double, 9>;
  _angular_velocity_covariance_type angular_velocity_covariance;
  using _linear_acceleration_zeroed_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _linear_acceleration_zeroed_type linear_acceleration_zeroed;
  using _linear_acceleration_raw_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _linear_acceleration_raw_type linear_acceleration_raw;
  using _linear_acceleration_covariance_type =
    std::array<double, 9>;
  _linear_acceleration_covariance_type linear_acceleration_covariance;
  using _nunchuk_acceleration_zeroed_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _nunchuk_acceleration_zeroed_type nunchuk_acceleration_zeroed;
  using _nunchuk_acceleration_raw_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _nunchuk_acceleration_raw_type nunchuk_acceleration_raw;
  using _nunchuk_joystick_zeroed_type =
    std::array<float, 2>;
  _nunchuk_joystick_zeroed_type nunchuk_joystick_zeroed;
  using _nunchuk_joystick_raw_type =
    std::array<float, 2>;
  _nunchuk_joystick_raw_type nunchuk_joystick_raw;
  using _buttons_type =
    std::array<bool, 11>;
  _buttons_type buttons;
  using _nunchuk_buttons_type =
    std::array<bool, 2>;
  _nunchuk_buttons_type nunchuk_buttons;
  using _leds_type =
    std::array<bool, 4>;
  _leds_type leds;
  using _rumble_type =
    bool;
  _rumble_type rumble;
  using _ir_tracking_type =
    std::vector<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>>>;
  _ir_tracking_type ir_tracking;
  using _raw_battery_type =
    float;
  _raw_battery_type raw_battery;
  using _percent_battery_type =
    float;
  _percent_battery_type percent_battery;
  using _zeroing_time_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _zeroing_time_type zeroing_time;
  using _errors_type =
    uint64_t;
  _errors_type errors;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__angular_velocity_zeroed(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->angular_velocity_zeroed = _arg;
    return *this;
  }
  Type & set__angular_velocity_raw(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->angular_velocity_raw = _arg;
    return *this;
  }
  Type & set__angular_velocity_covariance(
    const std::array<double, 9> & _arg)
  {
    this->angular_velocity_covariance = _arg;
    return *this;
  }
  Type & set__linear_acceleration_zeroed(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->linear_acceleration_zeroed = _arg;
    return *this;
  }
  Type & set__linear_acceleration_raw(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->linear_acceleration_raw = _arg;
    return *this;
  }
  Type & set__linear_acceleration_covariance(
    const std::array<double, 9> & _arg)
  {
    this->linear_acceleration_covariance = _arg;
    return *this;
  }
  Type & set__nunchuk_acceleration_zeroed(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->nunchuk_acceleration_zeroed = _arg;
    return *this;
  }
  Type & set__nunchuk_acceleration_raw(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->nunchuk_acceleration_raw = _arg;
    return *this;
  }
  Type & set__nunchuk_joystick_zeroed(
    const std::array<float, 2> & _arg)
  {
    this->nunchuk_joystick_zeroed = _arg;
    return *this;
  }
  Type & set__nunchuk_joystick_raw(
    const std::array<float, 2> & _arg)
  {
    this->nunchuk_joystick_raw = _arg;
    return *this;
  }
  Type & set__buttons(
    const std::array<bool, 11> & _arg)
  {
    this->buttons = _arg;
    return *this;
  }
  Type & set__nunchuk_buttons(
    const std::array<bool, 2> & _arg)
  {
    this->nunchuk_buttons = _arg;
    return *this;
  }
  Type & set__leds(
    const std::array<bool, 4> & _arg)
  {
    this->leds = _arg;
    return *this;
  }
  Type & set__rumble(
    const bool & _arg)
  {
    this->rumble = _arg;
    return *this;
  }
  Type & set__ir_tracking(
    const std::vector<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<wiimote_msgs::msg::IrSourceInfo_<ContainerAllocator>>> & _arg)
  {
    this->ir_tracking = _arg;
    return *this;
  }
  Type & set__raw_battery(
    const float & _arg)
  {
    this->raw_battery = _arg;
    return *this;
  }
  Type & set__percent_battery(
    const float & _arg)
  {
    this->percent_battery = _arg;
    return *this;
  }
  Type & set__zeroing_time(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->zeroing_time = _arg;
    return *this;
  }
  Type & set__errors(
    const uint64_t & _arg)
  {
    this->errors = _arg;
    return *this;
  }

  // constant declarations
  static constexpr int8_t INVALID =
    -1;
  static constexpr float INVALID_FLOAT =
    -1.0f;
  static constexpr int8_t MSG_BTN_1 =
    0;
  static constexpr int8_t MSG_BTN_2 =
    1;
  static constexpr int8_t MSG_BTN_A =
    2;
  static constexpr int8_t MSG_BTN_B =
    3;
  static constexpr int8_t MSG_BTN_PLUS =
    4;
  static constexpr int8_t MSG_BTN_MINUS =
    5;
  static constexpr int8_t MSG_BTN_LEFT =
    6;
  static constexpr int8_t MSG_BTN_RIGHT =
    7;
  static constexpr int8_t MSG_BTN_UP =
    8;
  static constexpr int8_t MSG_BTN_DOWN =
    9;
  static constexpr int8_t MSG_BTN_HOME =
    10;
  static constexpr int8_t MSG_BTN_Z =
    0;
  static constexpr int8_t MSG_BTN_C =
    1;
  static constexpr int8_t MSG_CLASSIC_BTN_X =
    0;
  static constexpr int8_t MSG_CLASSIC_BTN_Y =
    1;
  static constexpr int8_t MSG_CLASSIC_BTN_A =
    2;
  static constexpr int8_t MSG_CLASSIC_BTN_B =
    3;
  static constexpr int8_t MSG_CLASSIC_BTN_PLUS =
    4;
  static constexpr int8_t MSG_CLASSIC_BTN_MINUS =
    5;
  static constexpr int8_t MSG_CLASSIC_BTN_LEFT =
    6;
  static constexpr int8_t MSG_CLASSIC_BTN_RIGHT =
    7;
  static constexpr int8_t MSG_CLASSIC_BTN_UP =
    8;
  static constexpr int8_t MSG_CLASSIC_BTN_DOWN =
    9;
  static constexpr int8_t MSG_CLASSIC_BTN_HOME =
    10;
  static constexpr int8_t MSG_CLASSIC_BTN_L =
    11;
  static constexpr int8_t MSG_CLASSIC_BTN_R =
    12;
  static constexpr int8_t MSG_CLASSIC_BTN_ZL =
    13;
  static constexpr int8_t MSG_CLASSIC_BTN_ZR =
    14;

  // pointer types
  using RawPtr =
    wiimote_msgs::msg::State_<ContainerAllocator> *;
  using ConstRawPtr =
    const wiimote_msgs::msg::State_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<wiimote_msgs::msg::State_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<wiimote_msgs::msg::State_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      wiimote_msgs::msg::State_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<wiimote_msgs::msg::State_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      wiimote_msgs::msg::State_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<wiimote_msgs::msg::State_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<wiimote_msgs::msg::State_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<wiimote_msgs::msg::State_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__wiimote_msgs__msg__State
    std::shared_ptr<wiimote_msgs::msg::State_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__wiimote_msgs__msg__State
    std::shared_ptr<wiimote_msgs::msg::State_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const State_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->angular_velocity_zeroed != other.angular_velocity_zeroed) {
      return false;
    }
    if (this->angular_velocity_raw != other.angular_velocity_raw) {
      return false;
    }
    if (this->angular_velocity_covariance != other.angular_velocity_covariance) {
      return false;
    }
    if (this->linear_acceleration_zeroed != other.linear_acceleration_zeroed) {
      return false;
    }
    if (this->linear_acceleration_raw != other.linear_acceleration_raw) {
      return false;
    }
    if (this->linear_acceleration_covariance != other.linear_acceleration_covariance) {
      return false;
    }
    if (this->nunchuk_acceleration_zeroed != other.nunchuk_acceleration_zeroed) {
      return false;
    }
    if (this->nunchuk_acceleration_raw != other.nunchuk_acceleration_raw) {
      return false;
    }
    if (this->nunchuk_joystick_zeroed != other.nunchuk_joystick_zeroed) {
      return false;
    }
    if (this->nunchuk_joystick_raw != other.nunchuk_joystick_raw) {
      return false;
    }
    if (this->buttons != other.buttons) {
      return false;
    }
    if (this->nunchuk_buttons != other.nunchuk_buttons) {
      return false;
    }
    if (this->leds != other.leds) {
      return false;
    }
    if (this->rumble != other.rumble) {
      return false;
    }
    if (this->ir_tracking != other.ir_tracking) {
      return false;
    }
    if (this->raw_battery != other.raw_battery) {
      return false;
    }
    if (this->percent_battery != other.percent_battery) {
      return false;
    }
    if (this->zeroing_time != other.zeroing_time) {
      return false;
    }
    if (this->errors != other.errors) {
      return false;
    }
    return true;
  }
  bool operator!=(const State_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct State_

// alias to use template instance with default allocator
using State =
  wiimote_msgs::msg::State_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::INVALID;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr float State_<ContainerAllocator>::INVALID_FLOAT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_1;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_2;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_A;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_B;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_PLUS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_MINUS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_LEFT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_RIGHT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_UP;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_DOWN;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_HOME;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_Z;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_BTN_C;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_X;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_Y;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_A;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_B;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_PLUS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_MINUS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_LEFT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_RIGHT;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_UP;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_DOWN;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_HOME;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_L;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_R;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_ZL;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr int8_t State_<ContainerAllocator>::MSG_CLASSIC_BTN_ZR;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace wiimote_msgs

#endif  // WIIMOTE_MSGS__MSG__DETAIL__STATE__STRUCT_HPP_
