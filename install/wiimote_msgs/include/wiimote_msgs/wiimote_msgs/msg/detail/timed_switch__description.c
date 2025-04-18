// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from wiimote_msgs:msg/TimedSwitch.idl
// generated code does not contain a copyright notice

#include "wiimote_msgs/msg/detail/timed_switch__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_wiimote_msgs
const rosidl_type_hash_t *
wiimote_msgs__msg__TimedSwitch__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xbe, 0x79, 0x09, 0x31, 0x03, 0x43, 0x0f, 0x8e,
      0x59, 0x0b, 0x2b, 0x37, 0x54, 0xc2, 0x01, 0xab,
      0x1b, 0x9a, 0xee, 0xec, 0x18, 0x04, 0xc8, 0xc3,
      0x35, 0x58, 0xcb, 0xfc, 0x50, 0x0c, 0xe0, 0x94,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char wiimote_msgs__msg__TimedSwitch__TYPE_NAME[] = "wiimote_msgs/msg/TimedSwitch";

// Define type names, field names, and default values
static char wiimote_msgs__msg__TimedSwitch__FIELD_NAME__switch_mode[] = "switch_mode";
static char wiimote_msgs__msg__TimedSwitch__FIELD_NAME__num_cycles[] = "num_cycles";
static char wiimote_msgs__msg__TimedSwitch__FIELD_NAME__pulse_pattern[] = "pulse_pattern";

static rosidl_runtime_c__type_description__Field wiimote_msgs__msg__TimedSwitch__FIELDS[] = {
  {
    {wiimote_msgs__msg__TimedSwitch__FIELD_NAME__switch_mode, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__TimedSwitch__FIELD_NAME__num_cycles, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__TimedSwitch__FIELD_NAME__pulse_pattern, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
wiimote_msgs__msg__TimedSwitch__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {wiimote_msgs__msg__TimedSwitch__TYPE_NAME, 28, 28},
      {wiimote_msgs__msg__TimedSwitch__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# TimedSwitch allows sender to:\n"
  "#    o turn a switch on,\n"
  "#    o turn a switch off, and\n"
  "#    o repeat an on/off pattern forever or for a\n"
  "#          given number of times.\n"
  "# Fields (refer to definitions of constants in the definition body):\n"
  "#     o switch_mode:\n"
  "#         ON: turn on  (num_cycles and pulse_pattern fields are ignored)\n"
  "#        OFF: turn off (num_cycles and pulse_pattern fields are ignored)\n"
  "#  NO_CHANGE: leave LED in its current state\n"
  "#     REPEAT: repeat an on/off pattern for as long\n"
  "#             as is indicated in the num_cycles field. The\n"
  "#             pattern is defined in the pulse_pattern field.\n"
  "#\n"
  "#     o num_cycles:\n"
  "#          n>=0: run the pattern that is defined in pulse_pattern\n"
  "#                n times.\n"
  "#          n==FOREVER: run the pattern that is defined in pulse_pattern\n"
  "#                       until a new TimedSwitch message is sent.\n"
  "#\n"
  "#     o pulse_pattern:\n"
  "#          A series of time durations in fractions of a second. The\n"
  "#          first number is the duration for having the switch on.\n"
  "#          The second number is the duration for which the switch\n"
  "#          is off. The third is an 'on' period again, etc.\n"
  "#          A pattern is terminated with the end of the array.\n"
  "#\n"
  "#          Example: [1,1] specifies an on-off sequence of 1 second.\n"
  "\n"
  "int8 ON        =  1\n"
  "int8 OFF       =  0\n"
  "int8 NO_CHANGE = -2\n"
  "int8 REPEAT    = -1\n"
  "int8 FOREVER   = -1\n"
  "\n"
  "int8 switch_mode\n"
  "int32 num_cycles\n"
  "float32[] pulse_pattern";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
wiimote_msgs__msg__TimedSwitch__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {wiimote_msgs__msg__TimedSwitch__TYPE_NAME, 28, 28},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 1449, 1449},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
wiimote_msgs__msg__TimedSwitch__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *wiimote_msgs__msg__TimedSwitch__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
