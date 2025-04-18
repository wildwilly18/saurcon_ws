// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice
#include "wiimote_msgs/msg/detail/state__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `angular_velocity_zeroed`
// Member `angular_velocity_raw`
// Member `linear_acceleration_zeroed`
// Member `linear_acceleration_raw`
// Member `nunchuk_acceleration_zeroed`
// Member `nunchuk_acceleration_raw`
#include "geometry_msgs/msg/detail/vector3__functions.h"
// Member `ir_tracking`
#include "wiimote_msgs/msg/detail/ir_source_info__functions.h"
// Member `zeroing_time`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
wiimote_msgs__msg__State__init(wiimote_msgs__msg__State * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // angular_velocity_zeroed
  if (!geometry_msgs__msg__Vector3__init(&msg->angular_velocity_zeroed)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // angular_velocity_raw
  if (!geometry_msgs__msg__Vector3__init(&msg->angular_velocity_raw)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // angular_velocity_covariance
  // linear_acceleration_zeroed
  if (!geometry_msgs__msg__Vector3__init(&msg->linear_acceleration_zeroed)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // linear_acceleration_raw
  if (!geometry_msgs__msg__Vector3__init(&msg->linear_acceleration_raw)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // linear_acceleration_covariance
  // nunchuk_acceleration_zeroed
  if (!geometry_msgs__msg__Vector3__init(&msg->nunchuk_acceleration_zeroed)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // nunchuk_acceleration_raw
  if (!geometry_msgs__msg__Vector3__init(&msg->nunchuk_acceleration_raw)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // nunchuk_joystick_zeroed
  // nunchuk_joystick_raw
  // buttons
  // nunchuk_buttons
  // leds
  // rumble
  // ir_tracking
  if (!wiimote_msgs__msg__IrSourceInfo__Sequence__init(&msg->ir_tracking, 0)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // raw_battery
  // percent_battery
  // zeroing_time
  if (!builtin_interfaces__msg__Time__init(&msg->zeroing_time)) {
    wiimote_msgs__msg__State__fini(msg);
    return false;
  }
  // errors
  return true;
}

void
wiimote_msgs__msg__State__fini(wiimote_msgs__msg__State * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // angular_velocity_zeroed
  geometry_msgs__msg__Vector3__fini(&msg->angular_velocity_zeroed);
  // angular_velocity_raw
  geometry_msgs__msg__Vector3__fini(&msg->angular_velocity_raw);
  // angular_velocity_covariance
  // linear_acceleration_zeroed
  geometry_msgs__msg__Vector3__fini(&msg->linear_acceleration_zeroed);
  // linear_acceleration_raw
  geometry_msgs__msg__Vector3__fini(&msg->linear_acceleration_raw);
  // linear_acceleration_covariance
  // nunchuk_acceleration_zeroed
  geometry_msgs__msg__Vector3__fini(&msg->nunchuk_acceleration_zeroed);
  // nunchuk_acceleration_raw
  geometry_msgs__msg__Vector3__fini(&msg->nunchuk_acceleration_raw);
  // nunchuk_joystick_zeroed
  // nunchuk_joystick_raw
  // buttons
  // nunchuk_buttons
  // leds
  // rumble
  // ir_tracking
  wiimote_msgs__msg__IrSourceInfo__Sequence__fini(&msg->ir_tracking);
  // raw_battery
  // percent_battery
  // zeroing_time
  builtin_interfaces__msg__Time__fini(&msg->zeroing_time);
  // errors
}

bool
wiimote_msgs__msg__State__are_equal(const wiimote_msgs__msg__State * lhs, const wiimote_msgs__msg__State * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // angular_velocity_zeroed
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->angular_velocity_zeroed), &(rhs->angular_velocity_zeroed)))
  {
    return false;
  }
  // angular_velocity_raw
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->angular_velocity_raw), &(rhs->angular_velocity_raw)))
  {
    return false;
  }
  // angular_velocity_covariance
  for (size_t i = 0; i < 9; ++i) {
    if (lhs->angular_velocity_covariance[i] != rhs->angular_velocity_covariance[i]) {
      return false;
    }
  }
  // linear_acceleration_zeroed
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->linear_acceleration_zeroed), &(rhs->linear_acceleration_zeroed)))
  {
    return false;
  }
  // linear_acceleration_raw
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->linear_acceleration_raw), &(rhs->linear_acceleration_raw)))
  {
    return false;
  }
  // linear_acceleration_covariance
  for (size_t i = 0; i < 9; ++i) {
    if (lhs->linear_acceleration_covariance[i] != rhs->linear_acceleration_covariance[i]) {
      return false;
    }
  }
  // nunchuk_acceleration_zeroed
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->nunchuk_acceleration_zeroed), &(rhs->nunchuk_acceleration_zeroed)))
  {
    return false;
  }
  // nunchuk_acceleration_raw
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->nunchuk_acceleration_raw), &(rhs->nunchuk_acceleration_raw)))
  {
    return false;
  }
  // nunchuk_joystick_zeroed
  for (size_t i = 0; i < 2; ++i) {
    if (lhs->nunchuk_joystick_zeroed[i] != rhs->nunchuk_joystick_zeroed[i]) {
      return false;
    }
  }
  // nunchuk_joystick_raw
  for (size_t i = 0; i < 2; ++i) {
    if (lhs->nunchuk_joystick_raw[i] != rhs->nunchuk_joystick_raw[i]) {
      return false;
    }
  }
  // buttons
  for (size_t i = 0; i < 11; ++i) {
    if (lhs->buttons[i] != rhs->buttons[i]) {
      return false;
    }
  }
  // nunchuk_buttons
  for (size_t i = 0; i < 2; ++i) {
    if (lhs->nunchuk_buttons[i] != rhs->nunchuk_buttons[i]) {
      return false;
    }
  }
  // leds
  for (size_t i = 0; i < 4; ++i) {
    if (lhs->leds[i] != rhs->leds[i]) {
      return false;
    }
  }
  // rumble
  if (lhs->rumble != rhs->rumble) {
    return false;
  }
  // ir_tracking
  if (!wiimote_msgs__msg__IrSourceInfo__Sequence__are_equal(
      &(lhs->ir_tracking), &(rhs->ir_tracking)))
  {
    return false;
  }
  // raw_battery
  if (lhs->raw_battery != rhs->raw_battery) {
    return false;
  }
  // percent_battery
  if (lhs->percent_battery != rhs->percent_battery) {
    return false;
  }
  // zeroing_time
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->zeroing_time), &(rhs->zeroing_time)))
  {
    return false;
  }
  // errors
  if (lhs->errors != rhs->errors) {
    return false;
  }
  return true;
}

bool
wiimote_msgs__msg__State__copy(
  const wiimote_msgs__msg__State * input,
  wiimote_msgs__msg__State * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // angular_velocity_zeroed
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->angular_velocity_zeroed), &(output->angular_velocity_zeroed)))
  {
    return false;
  }
  // angular_velocity_raw
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->angular_velocity_raw), &(output->angular_velocity_raw)))
  {
    return false;
  }
  // angular_velocity_covariance
  for (size_t i = 0; i < 9; ++i) {
    output->angular_velocity_covariance[i] = input->angular_velocity_covariance[i];
  }
  // linear_acceleration_zeroed
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->linear_acceleration_zeroed), &(output->linear_acceleration_zeroed)))
  {
    return false;
  }
  // linear_acceleration_raw
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->linear_acceleration_raw), &(output->linear_acceleration_raw)))
  {
    return false;
  }
  // linear_acceleration_covariance
  for (size_t i = 0; i < 9; ++i) {
    output->linear_acceleration_covariance[i] = input->linear_acceleration_covariance[i];
  }
  // nunchuk_acceleration_zeroed
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->nunchuk_acceleration_zeroed), &(output->nunchuk_acceleration_zeroed)))
  {
    return false;
  }
  // nunchuk_acceleration_raw
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->nunchuk_acceleration_raw), &(output->nunchuk_acceleration_raw)))
  {
    return false;
  }
  // nunchuk_joystick_zeroed
  for (size_t i = 0; i < 2; ++i) {
    output->nunchuk_joystick_zeroed[i] = input->nunchuk_joystick_zeroed[i];
  }
  // nunchuk_joystick_raw
  for (size_t i = 0; i < 2; ++i) {
    output->nunchuk_joystick_raw[i] = input->nunchuk_joystick_raw[i];
  }
  // buttons
  for (size_t i = 0; i < 11; ++i) {
    output->buttons[i] = input->buttons[i];
  }
  // nunchuk_buttons
  for (size_t i = 0; i < 2; ++i) {
    output->nunchuk_buttons[i] = input->nunchuk_buttons[i];
  }
  // leds
  for (size_t i = 0; i < 4; ++i) {
    output->leds[i] = input->leds[i];
  }
  // rumble
  output->rumble = input->rumble;
  // ir_tracking
  if (!wiimote_msgs__msg__IrSourceInfo__Sequence__copy(
      &(input->ir_tracking), &(output->ir_tracking)))
  {
    return false;
  }
  // raw_battery
  output->raw_battery = input->raw_battery;
  // percent_battery
  output->percent_battery = input->percent_battery;
  // zeroing_time
  if (!builtin_interfaces__msg__Time__copy(
      &(input->zeroing_time), &(output->zeroing_time)))
  {
    return false;
  }
  // errors
  output->errors = input->errors;
  return true;
}

wiimote_msgs__msg__State *
wiimote_msgs__msg__State__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__State * msg = (wiimote_msgs__msg__State *)allocator.allocate(sizeof(wiimote_msgs__msg__State), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(wiimote_msgs__msg__State));
  bool success = wiimote_msgs__msg__State__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
wiimote_msgs__msg__State__destroy(wiimote_msgs__msg__State * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    wiimote_msgs__msg__State__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
wiimote_msgs__msg__State__Sequence__init(wiimote_msgs__msg__State__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__State * data = NULL;

  if (size) {
    data = (wiimote_msgs__msg__State *)allocator.zero_allocate(size, sizeof(wiimote_msgs__msg__State), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = wiimote_msgs__msg__State__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        wiimote_msgs__msg__State__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
wiimote_msgs__msg__State__Sequence__fini(wiimote_msgs__msg__State__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      wiimote_msgs__msg__State__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

wiimote_msgs__msg__State__Sequence *
wiimote_msgs__msg__State__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__State__Sequence * array = (wiimote_msgs__msg__State__Sequence *)allocator.allocate(sizeof(wiimote_msgs__msg__State__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = wiimote_msgs__msg__State__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
wiimote_msgs__msg__State__Sequence__destroy(wiimote_msgs__msg__State__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    wiimote_msgs__msg__State__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
wiimote_msgs__msg__State__Sequence__are_equal(const wiimote_msgs__msg__State__Sequence * lhs, const wiimote_msgs__msg__State__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!wiimote_msgs__msg__State__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
wiimote_msgs__msg__State__Sequence__copy(
  const wiimote_msgs__msg__State__Sequence * input,
  wiimote_msgs__msg__State__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(wiimote_msgs__msg__State);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    wiimote_msgs__msg__State * data =
      (wiimote_msgs__msg__State *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!wiimote_msgs__msg__State__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          wiimote_msgs__msg__State__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!wiimote_msgs__msg__State__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
