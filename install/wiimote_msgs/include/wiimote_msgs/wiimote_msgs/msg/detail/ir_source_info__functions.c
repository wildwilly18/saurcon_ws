// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice
#include "wiimote_msgs/msg/detail/ir_source_info__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
wiimote_msgs__msg__IrSourceInfo__init(wiimote_msgs__msg__IrSourceInfo * msg)
{
  if (!msg) {
    return false;
  }
  // x
  // y
  // ir_size
  return true;
}

void
wiimote_msgs__msg__IrSourceInfo__fini(wiimote_msgs__msg__IrSourceInfo * msg)
{
  if (!msg) {
    return;
  }
  // x
  // y
  // ir_size
}

bool
wiimote_msgs__msg__IrSourceInfo__are_equal(const wiimote_msgs__msg__IrSourceInfo * lhs, const wiimote_msgs__msg__IrSourceInfo * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // ir_size
  if (lhs->ir_size != rhs->ir_size) {
    return false;
  }
  return true;
}

bool
wiimote_msgs__msg__IrSourceInfo__copy(
  const wiimote_msgs__msg__IrSourceInfo * input,
  wiimote_msgs__msg__IrSourceInfo * output)
{
  if (!input || !output) {
    return false;
  }
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // ir_size
  output->ir_size = input->ir_size;
  return true;
}

wiimote_msgs__msg__IrSourceInfo *
wiimote_msgs__msg__IrSourceInfo__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__IrSourceInfo * msg = (wiimote_msgs__msg__IrSourceInfo *)allocator.allocate(sizeof(wiimote_msgs__msg__IrSourceInfo), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(wiimote_msgs__msg__IrSourceInfo));
  bool success = wiimote_msgs__msg__IrSourceInfo__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
wiimote_msgs__msg__IrSourceInfo__destroy(wiimote_msgs__msg__IrSourceInfo * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    wiimote_msgs__msg__IrSourceInfo__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
wiimote_msgs__msg__IrSourceInfo__Sequence__init(wiimote_msgs__msg__IrSourceInfo__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__IrSourceInfo * data = NULL;

  if (size) {
    data = (wiimote_msgs__msg__IrSourceInfo *)allocator.zero_allocate(size, sizeof(wiimote_msgs__msg__IrSourceInfo), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = wiimote_msgs__msg__IrSourceInfo__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        wiimote_msgs__msg__IrSourceInfo__fini(&data[i - 1]);
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
wiimote_msgs__msg__IrSourceInfo__Sequence__fini(wiimote_msgs__msg__IrSourceInfo__Sequence * array)
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
      wiimote_msgs__msg__IrSourceInfo__fini(&array->data[i]);
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

wiimote_msgs__msg__IrSourceInfo__Sequence *
wiimote_msgs__msg__IrSourceInfo__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  wiimote_msgs__msg__IrSourceInfo__Sequence * array = (wiimote_msgs__msg__IrSourceInfo__Sequence *)allocator.allocate(sizeof(wiimote_msgs__msg__IrSourceInfo__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = wiimote_msgs__msg__IrSourceInfo__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
wiimote_msgs__msg__IrSourceInfo__Sequence__destroy(wiimote_msgs__msg__IrSourceInfo__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    wiimote_msgs__msg__IrSourceInfo__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
wiimote_msgs__msg__IrSourceInfo__Sequence__are_equal(const wiimote_msgs__msg__IrSourceInfo__Sequence * lhs, const wiimote_msgs__msg__IrSourceInfo__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!wiimote_msgs__msg__IrSourceInfo__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
wiimote_msgs__msg__IrSourceInfo__Sequence__copy(
  const wiimote_msgs__msg__IrSourceInfo__Sequence * input,
  wiimote_msgs__msg__IrSourceInfo__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(wiimote_msgs__msg__IrSourceInfo);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    wiimote_msgs__msg__IrSourceInfo * data =
      (wiimote_msgs__msg__IrSourceInfo *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!wiimote_msgs__msg__IrSourceInfo__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          wiimote_msgs__msg__IrSourceInfo__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!wiimote_msgs__msg__IrSourceInfo__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
