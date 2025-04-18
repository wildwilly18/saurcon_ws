// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice
#include "wiimote_msgs/msg/detail/timed_switch__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `pulse_pattern`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
wiimote_msgs__msg__TimedSwitch__init(wiimote_msgs__msg__TimedSwitch * msg)
{
  if (!msg) {
    return false;
  }
  // switch_mode
  // num_cycles
  // pulse_pattern
  if (!rosidl_runtime_c__float__Sequence__init(&msg->pulse_pattern, 0)) {
    wiimote_msgs__msg__TimedSwitch__fini(msg);
    return false;
  }
  return true;
}

void
wiimote_msgs__msg__TimedSwitch__fini(wiimote_msgs__msg__TimedSwitch * msg)
{
  if (!msg) {
    return;
  }
  // switch_mode
  // num_cycles
  // pulse_pattern
  rosidl_runtime_c__float__Sequence__fini(&msg->pulse_pattern);
}

bool
wiimote_msgs__msg__TimedSwitch__are_equal(const wiimote_msgs__msg__TimedSwitch * lhs, const wiimote_msgs__msg__TimedSwitch * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // switch_mode
  if (lhs->switch_mode != rhs->switch_mode) {
    return false;
  }
  // num_cycles
  if (lhs->num_cycles != rhs->num_cycles) {
    return false;
  }
  // pulse_pattern
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->pulse_pattern), &(rhs->pulse_pattern)))
  {
    return false;
  }
  return true;
}

bool
wiimote_msgs__msg__TimedSwitch__copy(
  const wiimote_msgs__msg__TimedSwitch * input,
  wiimote_msgs__msg__TimedSwitch * output)
{
  if (!input || !output) {
    return false;
  }
  // switch_mode
  output->switch_mode = input->switch_mode;
  // num_cycles
  output->num_cycles = input->num_cycles;
  // pulse_pattern
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->pulse_pattern), &(output->pulse_pattern)))
  {
    return false;
  }
  return true;
}

wiimote_msgs__msg__TimedSwitch *
wiimote_msgs__msg__TimedSwitch__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__TimedSwitch * msg = (wiimote_msgs__msg__TimedSwitch *)allocator.allocate(sizeof(wiimote_msgs__msg__TimedSwitch), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(wiimote_msgs__msg__TimedSwitch));
  bool success = wiimote_msgs__msg__TimedSwitch__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
wiimote_msgs__msg__TimedSwitch__destroy(wiimote_msgs__msg__TimedSwitch * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    wiimote_msgs__msg__TimedSwitch__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
wiimote_msgs__msg__TimedSwitch__Sequence__init(wiimote_msgs__msg__TimedSwitch__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__TimedSwitch * data = NULL;

  if (size) {
    data = (wiimote_msgs__msg__TimedSwitch *)allocator.zero_allocate(size, sizeof(wiimote_msgs__msg__TimedSwitch), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = wiimote_msgs__msg__TimedSwitch__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        wiimote_msgs__msg__TimedSwitch__fini(&data[i - 1]);
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
wiimote_msgs__msg__TimedSwitch__Sequence__fini(wiimote_msgs__msg__TimedSwitch__Sequence * array)
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
      wiimote_msgs__msg__TimedSwitch__fini(&array->data[i]);
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

wiimote_msgs__msg__TimedSwitch__Sequence *
wiimote_msgs__msg__TimedSwitch__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__TimedSwitch__Sequence * array = (wiimote_msgs__msg__TimedSwitch__Sequence *)allocator.allocate(sizeof(wiimote_msgs__msg__TimedSwitch__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = wiimote_msgs__msg__TimedSwitch__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
wiimote_msgs__msg__TimedSwitch__Sequence__destroy(wiimote_msgs__msg__TimedSwitch__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    wiimote_msgs__msg__TimedSwitch__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
wiimote_msgs__msg__TimedSwitch__Sequence__are_equal(const wiimote_msgs__msg__TimedSwitch__Sequence * lhs, const wiimote_msgs__msg__TimedSwitch__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!wiimote_msgs__msg__TimedSwitch__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
wiimote_msgs__msg__TimedSwitch__Sequence__copy(
  const wiimote_msgs__msg__TimedSwitch__Sequence * input,
  wiimote_msgs__msg__TimedSwitch__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(wiimote_msgs__msg__TimedSwitch);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    wiimote_msgs__msg__TimedSwitch * data =
      (wiimote_msgs__msg__TimedSwitch *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!wiimote_msgs__msg__TimedSwitch__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          wiimote_msgs__msg__TimedSwitch__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!wiimote_msgs__msg__TimedSwitch__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
