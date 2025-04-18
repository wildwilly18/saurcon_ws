// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from wiimote_msgs:msg/IrSourceInfo.idl
// generated code does not contain a copyright notice

#include "wiimote_msgs/msg/detail/ir_source_info__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_wiimote_msgs
const rosidl_type_hash_t *
wiimote_msgs__msg__IrSourceInfo__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x8f, 0xbe, 0x86, 0x80, 0xf9, 0x4d, 0x53, 0x55,
      0x6b, 0xbc, 0x78, 0x3e, 0xce, 0x63, 0xfd, 0x60,
      0x4f, 0xe9, 0xa1, 0x0e, 0x4b, 0xb3, 0x69, 0x09,
      0xf6, 0x10, 0xf0, 0xa7, 0xb3, 0x0c, 0x3a, 0x12,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char wiimote_msgs__msg__IrSourceInfo__TYPE_NAME[] = "wiimote_msgs/msg/IrSourceInfo";

// Define type names, field names, and default values
static char wiimote_msgs__msg__IrSourceInfo__FIELD_NAME__x[] = "x";
static char wiimote_msgs__msg__IrSourceInfo__FIELD_NAME__y[] = "y";
static char wiimote_msgs__msg__IrSourceInfo__FIELD_NAME__ir_size[] = "ir_size";

static rosidl_runtime_c__type_description__Field wiimote_msgs__msg__IrSourceInfo__FIELDS[] = {
  {
    {wiimote_msgs__msg__IrSourceInfo__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__IrSourceInfo__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__IrSourceInfo__FIELD_NAME__ir_size, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
wiimote_msgs__msg__IrSourceInfo__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {wiimote_msgs__msg__IrSourceInfo__TYPE_NAME, 29, 29},
      {wiimote_msgs__msg__IrSourceInfo__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Sensor data pertaining to the Wiimote infrared camera.\n"
  "# This message contains data for one of the four infrared\n"
  "# light sources that the camera detects.\n"
  "#\n"
  "# Each light is specified with a 2D position and\n"
  "# a 'source magnitude' (ir_size). If the x dimension\n"
  "# is set to INVALID_FLOAT, then no light was detected for\n"
  "# the respective light. The Wiimote handles up to\n"
  "# four light sources, and the wiimote_controller software\n"
  "# is written to that limit as well.\n"
  "#\n"
  "# I am unsure what the 'ir_size' values represent.\n"
  "# They are described as 'source magnitude' in some places. I\n"
  "# *assume* this is signal amplitude, but it's unclear.\n"
  "# Note that current lowest level cwiid driver does not\n"
  "# seem to pass the ir_size value to the cwiid Wiimote.c.\n"
  "# For now this size will therefore be set INVALID\n"
  "\n"
  "float64 x\n"
  "float64 y\n"
  "int64 ir_size";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
wiimote_msgs__msg__IrSourceInfo__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {wiimote_msgs__msg__IrSourceInfo__TYPE_NAME, 29, 29},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 828, 828},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
wiimote_msgs__msg__IrSourceInfo__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *wiimote_msgs__msg__IrSourceInfo__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
