// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "wiimote_msgs/msg/ir_source_info.h"


#ifndef WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__STRUCT_H_
#define WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Struct defined in msg/IrSourceInfo in the package wiimote_msgs.
/**
  * Sensor data pertaining to the Wiimote infrared camera.
  * This message contains data for one of the four infrared
  * light sources that the camera detects.
  *
  * Each light is specified with a 2D position and
  * a 'source magnitude' (ir_size). If the x dimension
  * is set to INVALID_FLOAT, then no light was detected for
  * the respective light. The Wiimote handles up to
  * four light sources, and the wiimote_controller software
  * is written to that limit as well.
  *
  * I am unsure what the 'ir_size' values represent.
  * They are described as 'source magnitude' in some places. I
  * *assume* this is signal amplitude, but it's unclear.
  * Note that current lowest level cwiid driver does not
  * seem to pass the ir_size value to the cwiid Wiimote.c.
  * For now this size will therefore be set INVALID
 */
typedef struct wiimote_msgs__msg__IrSourceInfo
{
  double x;
  double y;
  int64_t ir_size;
} wiimote_msgs__msg__IrSourceInfo;

// Struct for a sequence of wiimote_msgs__msg__IrSourceInfo.
typedef struct wiimote_msgs__msg__IrSourceInfo__Sequence
{
  wiimote_msgs__msg__IrSourceInfo * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} wiimote_msgs__msg__IrSourceInfo__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // WIIMOTE_MSGS__MSG__DETAIL__IR_SOURCE_INFO__STRUCT_H_
