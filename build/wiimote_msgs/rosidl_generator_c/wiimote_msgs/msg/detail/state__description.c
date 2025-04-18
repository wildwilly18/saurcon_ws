// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from wiimote_msgs:msg/State.idl
// generated code does not contain a copyright notice

#include "wiimote_msgs/msg/detail/state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_wiimote_msgs
const rosidl_type_hash_t *
wiimote_msgs__msg__State__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x3f, 0x69, 0xce, 0x1b, 0x62, 0xf6, 0x2a, 0x61,
      0xbd, 0xe5, 0xfd, 0xdc, 0x26, 0x61, 0x46, 0x6f,
      0x4c, 0xa7, 0x6e, 0xc4, 0x18, 0x50, 0x6d, 0xef,
      0x40, 0xe8, 0x79, 0x32, 0xb5, 0xaa, 0x77, 0x5f,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "geometry_msgs/msg/detail/vector3__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "wiimote_msgs/msg/detail/ir_source_info__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Vector3__EXPECTED_HASH = {1, {
    0xcc, 0x12, 0xfe, 0x83, 0xe4, 0xc0, 0x27, 0x19,
    0xf1, 0xce, 0x80, 0x70, 0xbf, 0xd1, 0x4a, 0xec,
    0xd4, 0x0f, 0x75, 0xa9, 0x66, 0x96, 0xa6, 0x7a,
    0x2a, 0x1f, 0x37, 0xf7, 0xdb, 0xb0, 0x76, 0x5d,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
static const rosidl_type_hash_t wiimote_msgs__msg__IrSourceInfo__EXPECTED_HASH = {1, {
    0x8f, 0xbe, 0x86, 0x80, 0xf9, 0x4d, 0x53, 0x55,
    0x6b, 0xbc, 0x78, 0x3e, 0xce, 0x63, 0xfd, 0x60,
    0x4f, 0xe9, 0xa1, 0x0e, 0x4b, 0xb3, 0x69, 0x09,
    0xf6, 0x10, 0xf0, 0xa7, 0xb3, 0x0c, 0x3a, 0x12,
  }};
#endif

static char wiimote_msgs__msg__State__TYPE_NAME[] = "wiimote_msgs/msg/State";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char geometry_msgs__msg__Vector3__TYPE_NAME[] = "geometry_msgs/msg/Vector3";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";
static char wiimote_msgs__msg__IrSourceInfo__TYPE_NAME[] = "wiimote_msgs/msg/IrSourceInfo";

// Define type names, field names, and default values
static char wiimote_msgs__msg__State__FIELD_NAME__header[] = "header";
static char wiimote_msgs__msg__State__FIELD_NAME__angular_velocity_zeroed[] = "angular_velocity_zeroed";
static char wiimote_msgs__msg__State__FIELD_NAME__angular_velocity_raw[] = "angular_velocity_raw";
static char wiimote_msgs__msg__State__FIELD_NAME__angular_velocity_covariance[] = "angular_velocity_covariance";
static char wiimote_msgs__msg__State__FIELD_NAME__linear_acceleration_zeroed[] = "linear_acceleration_zeroed";
static char wiimote_msgs__msg__State__FIELD_NAME__linear_acceleration_raw[] = "linear_acceleration_raw";
static char wiimote_msgs__msg__State__FIELD_NAME__linear_acceleration_covariance[] = "linear_acceleration_covariance";
static char wiimote_msgs__msg__State__FIELD_NAME__nunchuk_acceleration_zeroed[] = "nunchuk_acceleration_zeroed";
static char wiimote_msgs__msg__State__FIELD_NAME__nunchuk_acceleration_raw[] = "nunchuk_acceleration_raw";
static char wiimote_msgs__msg__State__FIELD_NAME__nunchuk_joystick_zeroed[] = "nunchuk_joystick_zeroed";
static char wiimote_msgs__msg__State__FIELD_NAME__nunchuk_joystick_raw[] = "nunchuk_joystick_raw";
static char wiimote_msgs__msg__State__FIELD_NAME__buttons[] = "buttons";
static char wiimote_msgs__msg__State__FIELD_NAME__nunchuk_buttons[] = "nunchuk_buttons";
static char wiimote_msgs__msg__State__FIELD_NAME__leds[] = "leds";
static char wiimote_msgs__msg__State__FIELD_NAME__rumble[] = "rumble";
static char wiimote_msgs__msg__State__FIELD_NAME__ir_tracking[] = "ir_tracking";
static char wiimote_msgs__msg__State__FIELD_NAME__raw_battery[] = "raw_battery";
static char wiimote_msgs__msg__State__FIELD_NAME__percent_battery[] = "percent_battery";
static char wiimote_msgs__msg__State__FIELD_NAME__zeroing_time[] = "zeroing_time";
static char wiimote_msgs__msg__State__FIELD_NAME__errors[] = "errors";

static rosidl_runtime_c__type_description__Field wiimote_msgs__msg__State__FIELDS[] = {
  {
    {wiimote_msgs__msg__State__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__angular_velocity_zeroed, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__angular_velocity_raw, 20, 20},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__angular_velocity_covariance, 27, 27},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE_ARRAY,
      9,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__linear_acceleration_zeroed, 26, 26},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__linear_acceleration_raw, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__linear_acceleration_covariance, 30, 30},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE_ARRAY,
      9,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__nunchuk_acceleration_zeroed, 27, 27},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__nunchuk_acceleration_raw, 24, 24},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__nunchuk_joystick_zeroed, 23, 23},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__nunchuk_joystick_raw, 20, 20},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__buttons, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN_ARRAY,
      11,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__nunchuk_buttons, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__leds, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__rumble, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__ir_tracking, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {wiimote_msgs__msg__IrSourceInfo__TYPE_NAME, 29, 29},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__raw_battery, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__percent_battery, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__zeroing_time, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    },
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__State__FIELD_NAME__errors, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription wiimote_msgs__msg__State__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
  {
    {wiimote_msgs__msg__IrSourceInfo__TYPE_NAME, 29, 29},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
wiimote_msgs__msg__State__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {wiimote_msgs__msg__State__TYPE_NAME, 22, 22},
      {wiimote_msgs__msg__State__FIELDS, 20, 20},
    },
    {wiimote_msgs__msg__State__REFERENCED_TYPE_DESCRIPTIONS, 4, 4},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Vector3__EXPECTED_HASH, geometry_msgs__msg__Vector3__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Vector3__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&wiimote_msgs__msg__IrSourceInfo__EXPECTED_HASH, wiimote_msgs__msg__IrSourceInfo__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = wiimote_msgs__msg__IrSourceInfo__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "#\n"
  "#          Wiimote State message containing one complete Wiimote state\n"
  "\n"
  "# Note: For ease of manipulation this message often uses\n"
  "#       int8[] when a bit vector would work. One might\n"
  "#       wish to use uint8[], but then Python takes\n"
  "#       the respective structure as a string and disallows\n"
  "#       item assignment.\n"
  "\n"
  "int8    INVALID       = -1\n"
  "float32 INVALID_FLOAT = -1.0\n"
  "\n"
  "int8 MSG_BTN_1     = 0\n"
  "int8 MSG_BTN_2     = 1\n"
  "int8 MSG_BTN_A     = 2\n"
  "int8 MSG_BTN_B     = 3\n"
  "int8 MSG_BTN_PLUS  = 4\n"
  "int8 MSG_BTN_MINUS = 5\n"
  "int8 MSG_BTN_LEFT  = 6\n"
  "int8 MSG_BTN_RIGHT = 7\n"
  "int8 MSG_BTN_UP    = 8\n"
  "int8 MSG_BTN_DOWN  = 9\n"
  "int8 MSG_BTN_HOME  = 10\n"
  "int8 MSG_BTN_Z     = 0\n"
  "int8 MSG_BTN_C     = 1\n"
  "int8 MSG_CLASSIC_BTN_X       = 0\n"
  "int8 MSG_CLASSIC_BTN_Y       = 1\n"
  "int8 MSG_CLASSIC_BTN_A       = 2\n"
  "int8 MSG_CLASSIC_BTN_B       = 3\n"
  "int8 MSG_CLASSIC_BTN_PLUS    = 4\n"
  "int8 MSG_CLASSIC_BTN_MINUS   = 5\n"
  "int8 MSG_CLASSIC_BTN_LEFT    = 6\n"
  "int8 MSG_CLASSIC_BTN_RIGHT   = 7\n"
  "int8 MSG_CLASSIC_BTN_UP      = 8\n"
  "int8 MSG_CLASSIC_BTN_DOWN    = 9\n"
  "int8 MSG_CLASSIC_BTN_HOME    = 10\n"
  "int8 MSG_CLASSIC_BTN_L       = 11\n"
  "int8 MSG_CLASSIC_BTN_R       = 12\n"
  "int8 MSG_CLASSIC_BTN_ZL      = 13\n"
  "int8 MSG_CLASSIC_BTN_ZR      = 14\n"
  "\n"
  "#-----------------------------\n"
  "# Header\n"
  "#----------------------\n"
  "\n"
  "std_msgs/Header header\n"
  "\n"
  "#----------------------\n"
  "# Gyro reading\n"
  "#-----------------------------\n"
  "# In radians/sec. If reading is invalid,\n"
  "# for instance b/c no gyro is attached to the Wii, then\n"
  "# set first element of covariance to -1 (same as imu_data.msg):\n"
  "# Covariance matrix (roll, pitch, yaw) in radians^2/sec^2.\n"
  "\n"
  "geometry_msgs/Vector3 angular_velocity_zeroed\n"
  "geometry_msgs/Vector3 angular_velocity_raw\n"
  "float64[9] angular_velocity_covariance\n"
  "\n"
  "#----------------------\n"
  "# Accelerometer reading\n"
  "#-----------------------------\n"
  "# Acceleration in m/sec^2. Covariance matrix\n"
  "# (x,y,z) in m^2/sec^4.  (all same as imu_data.msg)\n"
  "\n"
  "geometry_msgs/Vector3 linear_acceleration_zeroed\n"
  "geometry_msgs/Vector3 linear_acceleration_raw\n"
  "float64[9] linear_acceleration_covariance\n"
  "\n"
  "#------------------------------\n"
  "# Nunchuk Accelerometer reading\n"
  "#------------------------------\n"
  "geometry_msgs/Vector3 nunchuk_acceleration_zeroed\n"
  "geometry_msgs/Vector3 nunchuk_acceleration_raw\n"
  "\n"
  "#-----------------\n"
  "# Nunchuk Joystick\n"
  "#-----------------\n"
  "float32[2] nunchuk_joystick_zeroed\n"
  "float32[2] nunchuk_joystick_raw\n"
  "\n"
  "#----------------------\n"
  "# Wiimote buttons\n"
  "#-----------------------------\n"
  "# Mappings from Wiimote button name\n"
  "# to array position are defined above.\n"
  "#\n"
  "bool[11] buttons\n"
  "bool[2] nunchuk_buttons\n"
  "\n"
  "#----------------------\n"
  "# Wiimote LED states:\n"
  "#-----------------------------\n"
  "\n"
  "bool[4] leds\n"
  "\n"
  "#----------------------\n"
  "# Wiimote Rumble\n"
  "#-----------------------------\n"
  "# State (True or False)\n"
  "\n"
  "bool rumble\n"
  "\n"
  "#----------------------\n"
  "# IR Light sensor (Camera)\n"
  "#-----------------------------\n"
  "# The Wiimote handles up to four light sources, \n"
  "# and the wiimote_controller software is written to\n"
  "# that limit as well. For future expansion\n"
  "# we make the following array extensible, rather\n"
  "# than locking its length down to four:\n"
  "\n"
  "wiimote_msgs/IrSourceInfo[] ir_tracking\n"
  "\n"
  "#----------------------\n"
  "# Wiimote battery\n"
  "#-----------------------------\n"
  "# A battery reading consists of two numbers: \n"
  "# the battery percentage, and the raw reading.\n"
  "# Maximum battery is 208 units (unknown how this\n"
  "# relates to electrical properties): \n"
  "\n"
  "float32 raw_battery\n"
  "float32 percent_battery\n"
  "\n"
  "#----------------------\n"
  "# Time of most recent zeroing:\n"
  "#-----------------------------\n"
  "\n"
  "builtin_interfaces/Time zeroing_time\n"
  "\n"
  "#----------------------\n"
  "# Error vector\n"
  "#-----------------------------\n"
  "# For error condition definitions see wiimoteConstants.py\n"
  "# Value of zero means all is well. (Currently NOT used).\n"
  "\n"
  "uint64 errors";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
wiimote_msgs__msg__State__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {wiimote_msgs__msg__State__TYPE_NAME, 22, 22},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 3698, 3698},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
wiimote_msgs__msg__State__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[5];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 5, 5};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *wiimote_msgs__msg__State__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Vector3__get_individual_type_description_source(NULL);
    sources[3] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[4] = *wiimote_msgs__msg__IrSourceInfo__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
