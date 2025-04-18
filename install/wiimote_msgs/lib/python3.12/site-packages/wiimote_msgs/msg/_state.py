# generated from rosidl_generator_py/resource/_idl.py.em
# with input from wiimote_msgs:msg/State.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

# Member 'angular_velocity_covariance'
# Member 'linear_acceleration_covariance'
# Member 'nunchuk_joystick_zeroed'
# Member 'nunchuk_joystick_raw'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_State(type):
    """Metaclass of message 'State'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'INVALID': -1,
        'INVALID_FLOAT': -1.0,
        'MSG_BTN_1': 0,
        'MSG_BTN_2': 1,
        'MSG_BTN_A': 2,
        'MSG_BTN_B': 3,
        'MSG_BTN_PLUS': 4,
        'MSG_BTN_MINUS': 5,
        'MSG_BTN_LEFT': 6,
        'MSG_BTN_RIGHT': 7,
        'MSG_BTN_UP': 8,
        'MSG_BTN_DOWN': 9,
        'MSG_BTN_HOME': 10,
        'MSG_BTN_Z': 0,
        'MSG_BTN_C': 1,
        'MSG_CLASSIC_BTN_X': 0,
        'MSG_CLASSIC_BTN_Y': 1,
        'MSG_CLASSIC_BTN_A': 2,
        'MSG_CLASSIC_BTN_B': 3,
        'MSG_CLASSIC_BTN_PLUS': 4,
        'MSG_CLASSIC_BTN_MINUS': 5,
        'MSG_CLASSIC_BTN_LEFT': 6,
        'MSG_CLASSIC_BTN_RIGHT': 7,
        'MSG_CLASSIC_BTN_UP': 8,
        'MSG_CLASSIC_BTN_DOWN': 9,
        'MSG_CLASSIC_BTN_HOME': 10,
        'MSG_CLASSIC_BTN_L': 11,
        'MSG_CLASSIC_BTN_R': 12,
        'MSG_CLASSIC_BTN_ZL': 13,
        'MSG_CLASSIC_BTN_ZR': 14,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('wiimote_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'wiimote_msgs.msg.State')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__state
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__state
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__state
            cls._TYPE_SUPPORT = module.type_support_msg__msg__state
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__state

            from builtin_interfaces.msg import Time
            if Time.__class__._TYPE_SUPPORT is None:
                Time.__class__.__import_type_support__()

            from geometry_msgs.msg import Vector3
            if Vector3.__class__._TYPE_SUPPORT is None:
                Vector3.__class__.__import_type_support__()

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

            from wiimote_msgs.msg import IrSourceInfo
            if IrSourceInfo.__class__._TYPE_SUPPORT is None:
                IrSourceInfo.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'INVALID': cls.__constants['INVALID'],
            'INVALID_FLOAT': cls.__constants['INVALID_FLOAT'],
            'MSG_BTN_1': cls.__constants['MSG_BTN_1'],
            'MSG_BTN_2': cls.__constants['MSG_BTN_2'],
            'MSG_BTN_A': cls.__constants['MSG_BTN_A'],
            'MSG_BTN_B': cls.__constants['MSG_BTN_B'],
            'MSG_BTN_PLUS': cls.__constants['MSG_BTN_PLUS'],
            'MSG_BTN_MINUS': cls.__constants['MSG_BTN_MINUS'],
            'MSG_BTN_LEFT': cls.__constants['MSG_BTN_LEFT'],
            'MSG_BTN_RIGHT': cls.__constants['MSG_BTN_RIGHT'],
            'MSG_BTN_UP': cls.__constants['MSG_BTN_UP'],
            'MSG_BTN_DOWN': cls.__constants['MSG_BTN_DOWN'],
            'MSG_BTN_HOME': cls.__constants['MSG_BTN_HOME'],
            'MSG_BTN_Z': cls.__constants['MSG_BTN_Z'],
            'MSG_BTN_C': cls.__constants['MSG_BTN_C'],
            'MSG_CLASSIC_BTN_X': cls.__constants['MSG_CLASSIC_BTN_X'],
            'MSG_CLASSIC_BTN_Y': cls.__constants['MSG_CLASSIC_BTN_Y'],
            'MSG_CLASSIC_BTN_A': cls.__constants['MSG_CLASSIC_BTN_A'],
            'MSG_CLASSIC_BTN_B': cls.__constants['MSG_CLASSIC_BTN_B'],
            'MSG_CLASSIC_BTN_PLUS': cls.__constants['MSG_CLASSIC_BTN_PLUS'],
            'MSG_CLASSIC_BTN_MINUS': cls.__constants['MSG_CLASSIC_BTN_MINUS'],
            'MSG_CLASSIC_BTN_LEFT': cls.__constants['MSG_CLASSIC_BTN_LEFT'],
            'MSG_CLASSIC_BTN_RIGHT': cls.__constants['MSG_CLASSIC_BTN_RIGHT'],
            'MSG_CLASSIC_BTN_UP': cls.__constants['MSG_CLASSIC_BTN_UP'],
            'MSG_CLASSIC_BTN_DOWN': cls.__constants['MSG_CLASSIC_BTN_DOWN'],
            'MSG_CLASSIC_BTN_HOME': cls.__constants['MSG_CLASSIC_BTN_HOME'],
            'MSG_CLASSIC_BTN_L': cls.__constants['MSG_CLASSIC_BTN_L'],
            'MSG_CLASSIC_BTN_R': cls.__constants['MSG_CLASSIC_BTN_R'],
            'MSG_CLASSIC_BTN_ZL': cls.__constants['MSG_CLASSIC_BTN_ZL'],
            'MSG_CLASSIC_BTN_ZR': cls.__constants['MSG_CLASSIC_BTN_ZR'],
        }

    @property
    def INVALID(self):
        """Message constant 'INVALID'."""
        return Metaclass_State.__constants['INVALID']

    @property
    def INVALID_FLOAT(self):
        """Message constant 'INVALID_FLOAT'."""
        return Metaclass_State.__constants['INVALID_FLOAT']

    @property
    def MSG_BTN_1(self):
        """Message constant 'MSG_BTN_1'."""
        return Metaclass_State.__constants['MSG_BTN_1']

    @property
    def MSG_BTN_2(self):
        """Message constant 'MSG_BTN_2'."""
        return Metaclass_State.__constants['MSG_BTN_2']

    @property
    def MSG_BTN_A(self):
        """Message constant 'MSG_BTN_A'."""
        return Metaclass_State.__constants['MSG_BTN_A']

    @property
    def MSG_BTN_B(self):
        """Message constant 'MSG_BTN_B'."""
        return Metaclass_State.__constants['MSG_BTN_B']

    @property
    def MSG_BTN_PLUS(self):
        """Message constant 'MSG_BTN_PLUS'."""
        return Metaclass_State.__constants['MSG_BTN_PLUS']

    @property
    def MSG_BTN_MINUS(self):
        """Message constant 'MSG_BTN_MINUS'."""
        return Metaclass_State.__constants['MSG_BTN_MINUS']

    @property
    def MSG_BTN_LEFT(self):
        """Message constant 'MSG_BTN_LEFT'."""
        return Metaclass_State.__constants['MSG_BTN_LEFT']

    @property
    def MSG_BTN_RIGHT(self):
        """Message constant 'MSG_BTN_RIGHT'."""
        return Metaclass_State.__constants['MSG_BTN_RIGHT']

    @property
    def MSG_BTN_UP(self):
        """Message constant 'MSG_BTN_UP'."""
        return Metaclass_State.__constants['MSG_BTN_UP']

    @property
    def MSG_BTN_DOWN(self):
        """Message constant 'MSG_BTN_DOWN'."""
        return Metaclass_State.__constants['MSG_BTN_DOWN']

    @property
    def MSG_BTN_HOME(self):
        """Message constant 'MSG_BTN_HOME'."""
        return Metaclass_State.__constants['MSG_BTN_HOME']

    @property
    def MSG_BTN_Z(self):
        """Message constant 'MSG_BTN_Z'."""
        return Metaclass_State.__constants['MSG_BTN_Z']

    @property
    def MSG_BTN_C(self):
        """Message constant 'MSG_BTN_C'."""
        return Metaclass_State.__constants['MSG_BTN_C']

    @property
    def MSG_CLASSIC_BTN_X(self):
        """Message constant 'MSG_CLASSIC_BTN_X'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_X']

    @property
    def MSG_CLASSIC_BTN_Y(self):
        """Message constant 'MSG_CLASSIC_BTN_Y'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_Y']

    @property
    def MSG_CLASSIC_BTN_A(self):
        """Message constant 'MSG_CLASSIC_BTN_A'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_A']

    @property
    def MSG_CLASSIC_BTN_B(self):
        """Message constant 'MSG_CLASSIC_BTN_B'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_B']

    @property
    def MSG_CLASSIC_BTN_PLUS(self):
        """Message constant 'MSG_CLASSIC_BTN_PLUS'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_PLUS']

    @property
    def MSG_CLASSIC_BTN_MINUS(self):
        """Message constant 'MSG_CLASSIC_BTN_MINUS'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_MINUS']

    @property
    def MSG_CLASSIC_BTN_LEFT(self):
        """Message constant 'MSG_CLASSIC_BTN_LEFT'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_LEFT']

    @property
    def MSG_CLASSIC_BTN_RIGHT(self):
        """Message constant 'MSG_CLASSIC_BTN_RIGHT'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_RIGHT']

    @property
    def MSG_CLASSIC_BTN_UP(self):
        """Message constant 'MSG_CLASSIC_BTN_UP'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_UP']

    @property
    def MSG_CLASSIC_BTN_DOWN(self):
        """Message constant 'MSG_CLASSIC_BTN_DOWN'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_DOWN']

    @property
    def MSG_CLASSIC_BTN_HOME(self):
        """Message constant 'MSG_CLASSIC_BTN_HOME'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_HOME']

    @property
    def MSG_CLASSIC_BTN_L(self):
        """Message constant 'MSG_CLASSIC_BTN_L'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_L']

    @property
    def MSG_CLASSIC_BTN_R(self):
        """Message constant 'MSG_CLASSIC_BTN_R'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_R']

    @property
    def MSG_CLASSIC_BTN_ZL(self):
        """Message constant 'MSG_CLASSIC_BTN_ZL'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_ZL']

    @property
    def MSG_CLASSIC_BTN_ZR(self):
        """Message constant 'MSG_CLASSIC_BTN_ZR'."""
        return Metaclass_State.__constants['MSG_CLASSIC_BTN_ZR']


class State(metaclass=Metaclass_State):
    """
    Message class 'State'.

    Constants:
      INVALID
      INVALID_FLOAT
      MSG_BTN_1
      MSG_BTN_2
      MSG_BTN_A
      MSG_BTN_B
      MSG_BTN_PLUS
      MSG_BTN_MINUS
      MSG_BTN_LEFT
      MSG_BTN_RIGHT
      MSG_BTN_UP
      MSG_BTN_DOWN
      MSG_BTN_HOME
      MSG_BTN_Z
      MSG_BTN_C
      MSG_CLASSIC_BTN_X
      MSG_CLASSIC_BTN_Y
      MSG_CLASSIC_BTN_A
      MSG_CLASSIC_BTN_B
      MSG_CLASSIC_BTN_PLUS
      MSG_CLASSIC_BTN_MINUS
      MSG_CLASSIC_BTN_LEFT
      MSG_CLASSIC_BTN_RIGHT
      MSG_CLASSIC_BTN_UP
      MSG_CLASSIC_BTN_DOWN
      MSG_CLASSIC_BTN_HOME
      MSG_CLASSIC_BTN_L
      MSG_CLASSIC_BTN_R
      MSG_CLASSIC_BTN_ZL
      MSG_CLASSIC_BTN_ZR
    """

    __slots__ = [
        '_header',
        '_angular_velocity_zeroed',
        '_angular_velocity_raw',
        '_angular_velocity_covariance',
        '_linear_acceleration_zeroed',
        '_linear_acceleration_raw',
        '_linear_acceleration_covariance',
        '_nunchuk_acceleration_zeroed',
        '_nunchuk_acceleration_raw',
        '_nunchuk_joystick_zeroed',
        '_nunchuk_joystick_raw',
        '_buttons',
        '_nunchuk_buttons',
        '_leds',
        '_rumble',
        '_ir_tracking',
        '_raw_battery',
        '_percent_battery',
        '_zeroing_time',
        '_errors',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'angular_velocity_zeroed': 'geometry_msgs/Vector3',
        'angular_velocity_raw': 'geometry_msgs/Vector3',
        'angular_velocity_covariance': 'double[9]',
        'linear_acceleration_zeroed': 'geometry_msgs/Vector3',
        'linear_acceleration_raw': 'geometry_msgs/Vector3',
        'linear_acceleration_covariance': 'double[9]',
        'nunchuk_acceleration_zeroed': 'geometry_msgs/Vector3',
        'nunchuk_acceleration_raw': 'geometry_msgs/Vector3',
        'nunchuk_joystick_zeroed': 'float[2]',
        'nunchuk_joystick_raw': 'float[2]',
        'buttons': 'boolean[11]',
        'nunchuk_buttons': 'boolean[2]',
        'leds': 'boolean[4]',
        'rumble': 'boolean',
        'ir_tracking': 'sequence<wiimote_msgs/IrSourceInfo>',
        'raw_battery': 'float',
        'percent_battery': 'float',
        'zeroing_time': 'builtin_interfaces/Time',
        'errors': 'uint64',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Vector3'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Vector3'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('double'), 9),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Vector3'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Vector3'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('double'), 9),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Vector3'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Vector3'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('float'), 2),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('float'), 2),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('boolean'), 11),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('boolean'), 2),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('boolean'), 4),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['wiimote_msgs', 'msg'], 'IrSourceInfo')),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Time'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        from geometry_msgs.msg import Vector3
        self.angular_velocity_zeroed = kwargs.get('angular_velocity_zeroed', Vector3())
        from geometry_msgs.msg import Vector3
        self.angular_velocity_raw = kwargs.get('angular_velocity_raw', Vector3())
        if 'angular_velocity_covariance' not in kwargs:
            self.angular_velocity_covariance = numpy.zeros(9, dtype=numpy.float64)
        else:
            self.angular_velocity_covariance = numpy.array(kwargs.get('angular_velocity_covariance'), dtype=numpy.float64)
            assert self.angular_velocity_covariance.shape == (9, )
        from geometry_msgs.msg import Vector3
        self.linear_acceleration_zeroed = kwargs.get('linear_acceleration_zeroed', Vector3())
        from geometry_msgs.msg import Vector3
        self.linear_acceleration_raw = kwargs.get('linear_acceleration_raw', Vector3())
        if 'linear_acceleration_covariance' not in kwargs:
            self.linear_acceleration_covariance = numpy.zeros(9, dtype=numpy.float64)
        else:
            self.linear_acceleration_covariance = numpy.array(kwargs.get('linear_acceleration_covariance'), dtype=numpy.float64)
            assert self.linear_acceleration_covariance.shape == (9, )
        from geometry_msgs.msg import Vector3
        self.nunchuk_acceleration_zeroed = kwargs.get('nunchuk_acceleration_zeroed', Vector3())
        from geometry_msgs.msg import Vector3
        self.nunchuk_acceleration_raw = kwargs.get('nunchuk_acceleration_raw', Vector3())
        if 'nunchuk_joystick_zeroed' not in kwargs:
            self.nunchuk_joystick_zeroed = numpy.zeros(2, dtype=numpy.float32)
        else:
            self.nunchuk_joystick_zeroed = numpy.array(kwargs.get('nunchuk_joystick_zeroed'), dtype=numpy.float32)
            assert self.nunchuk_joystick_zeroed.shape == (2, )
        if 'nunchuk_joystick_raw' not in kwargs:
            self.nunchuk_joystick_raw = numpy.zeros(2, dtype=numpy.float32)
        else:
            self.nunchuk_joystick_raw = numpy.array(kwargs.get('nunchuk_joystick_raw'), dtype=numpy.float32)
            assert self.nunchuk_joystick_raw.shape == (2, )
        self.buttons = kwargs.get(
            'buttons',
            [bool() for x in range(11)]
        )
        self.nunchuk_buttons = kwargs.get(
            'nunchuk_buttons',
            [bool() for x in range(2)]
        )
        self.leds = kwargs.get(
            'leds',
            [bool() for x in range(4)]
        )
        self.rumble = kwargs.get('rumble', bool())
        self.ir_tracking = kwargs.get('ir_tracking', [])
        self.raw_battery = kwargs.get('raw_battery', float())
        self.percent_battery = kwargs.get('percent_battery', float())
        from builtin_interfaces.msg import Time
        self.zeroing_time = kwargs.get('zeroing_time', Time())
        self.errors = kwargs.get('errors', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.header != other.header:
            return False
        if self.angular_velocity_zeroed != other.angular_velocity_zeroed:
            return False
        if self.angular_velocity_raw != other.angular_velocity_raw:
            return False
        if all(self.angular_velocity_covariance != other.angular_velocity_covariance):
            return False
        if self.linear_acceleration_zeroed != other.linear_acceleration_zeroed:
            return False
        if self.linear_acceleration_raw != other.linear_acceleration_raw:
            return False
        if all(self.linear_acceleration_covariance != other.linear_acceleration_covariance):
            return False
        if self.nunchuk_acceleration_zeroed != other.nunchuk_acceleration_zeroed:
            return False
        if self.nunchuk_acceleration_raw != other.nunchuk_acceleration_raw:
            return False
        if all(self.nunchuk_joystick_zeroed != other.nunchuk_joystick_zeroed):
            return False
        if all(self.nunchuk_joystick_raw != other.nunchuk_joystick_raw):
            return False
        if self.buttons != other.buttons:
            return False
        if self.nunchuk_buttons != other.nunchuk_buttons:
            return False
        if self.leds != other.leds:
            return False
        if self.rumble != other.rumble:
            return False
        if self.ir_tracking != other.ir_tracking:
            return False
        if self.raw_battery != other.raw_battery:
            return False
        if self.percent_battery != other.percent_battery:
            return False
        if self.zeroing_time != other.zeroing_time:
            return False
        if self.errors != other.errors:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if self._check_fields:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def angular_velocity_zeroed(self):
        """Message field 'angular_velocity_zeroed'."""
        return self._angular_velocity_zeroed

    @angular_velocity_zeroed.setter
    def angular_velocity_zeroed(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Vector3
            assert \
                isinstance(value, Vector3), \
                "The 'angular_velocity_zeroed' field must be a sub message of type 'Vector3'"
        self._angular_velocity_zeroed = value

    @builtins.property
    def angular_velocity_raw(self):
        """Message field 'angular_velocity_raw'."""
        return self._angular_velocity_raw

    @angular_velocity_raw.setter
    def angular_velocity_raw(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Vector3
            assert \
                isinstance(value, Vector3), \
                "The 'angular_velocity_raw' field must be a sub message of type 'Vector3'"
        self._angular_velocity_raw = value

    @builtins.property
    def angular_velocity_covariance(self):
        """Message field 'angular_velocity_covariance'."""
        return self._angular_velocity_covariance

    @angular_velocity_covariance.setter
    def angular_velocity_covariance(self, value):
        if self._check_fields:
            if isinstance(value, numpy.ndarray):
                assert value.dtype == numpy.float64, \
                    "The 'angular_velocity_covariance' numpy.ndarray() must have the dtype of 'numpy.float64'"
                assert value.size == 9, \
                    "The 'angular_velocity_covariance' numpy.ndarray() must have a size of 9"
                self._angular_velocity_covariance = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 9 and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -1.7976931348623157e+308 or val > 1.7976931348623157e+308) or math.isinf(val) for val in value)), \
                "The 'angular_velocity_covariance' field must be a set or sequence with length 9 and each value of type 'float' and each double in [-179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000, 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000]"
        self._angular_velocity_covariance = numpy.array(value, dtype=numpy.float64)

    @builtins.property
    def linear_acceleration_zeroed(self):
        """Message field 'linear_acceleration_zeroed'."""
        return self._linear_acceleration_zeroed

    @linear_acceleration_zeroed.setter
    def linear_acceleration_zeroed(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Vector3
            assert \
                isinstance(value, Vector3), \
                "The 'linear_acceleration_zeroed' field must be a sub message of type 'Vector3'"
        self._linear_acceleration_zeroed = value

    @builtins.property
    def linear_acceleration_raw(self):
        """Message field 'linear_acceleration_raw'."""
        return self._linear_acceleration_raw

    @linear_acceleration_raw.setter
    def linear_acceleration_raw(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Vector3
            assert \
                isinstance(value, Vector3), \
                "The 'linear_acceleration_raw' field must be a sub message of type 'Vector3'"
        self._linear_acceleration_raw = value

    @builtins.property
    def linear_acceleration_covariance(self):
        """Message field 'linear_acceleration_covariance'."""
        return self._linear_acceleration_covariance

    @linear_acceleration_covariance.setter
    def linear_acceleration_covariance(self, value):
        if self._check_fields:
            if isinstance(value, numpy.ndarray):
                assert value.dtype == numpy.float64, \
                    "The 'linear_acceleration_covariance' numpy.ndarray() must have the dtype of 'numpy.float64'"
                assert value.size == 9, \
                    "The 'linear_acceleration_covariance' numpy.ndarray() must have a size of 9"
                self._linear_acceleration_covariance = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 9 and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -1.7976931348623157e+308 or val > 1.7976931348623157e+308) or math.isinf(val) for val in value)), \
                "The 'linear_acceleration_covariance' field must be a set or sequence with length 9 and each value of type 'float' and each double in [-179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000, 179769313486231570814527423731704356798070567525844996598917476803157260780028538760589558632766878171540458953514382464234321326889464182768467546703537516986049910576551282076245490090389328944075868508455133942304583236903222948165808559332123348274797826204144723168738177180919299881250404026184124858368.000000]"
        self._linear_acceleration_covariance = numpy.array(value, dtype=numpy.float64)

    @builtins.property
    def nunchuk_acceleration_zeroed(self):
        """Message field 'nunchuk_acceleration_zeroed'."""
        return self._nunchuk_acceleration_zeroed

    @nunchuk_acceleration_zeroed.setter
    def nunchuk_acceleration_zeroed(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Vector3
            assert \
                isinstance(value, Vector3), \
                "The 'nunchuk_acceleration_zeroed' field must be a sub message of type 'Vector3'"
        self._nunchuk_acceleration_zeroed = value

    @builtins.property
    def nunchuk_acceleration_raw(self):
        """Message field 'nunchuk_acceleration_raw'."""
        return self._nunchuk_acceleration_raw

    @nunchuk_acceleration_raw.setter
    def nunchuk_acceleration_raw(self, value):
        if self._check_fields:
            from geometry_msgs.msg import Vector3
            assert \
                isinstance(value, Vector3), \
                "The 'nunchuk_acceleration_raw' field must be a sub message of type 'Vector3'"
        self._nunchuk_acceleration_raw = value

    @builtins.property
    def nunchuk_joystick_zeroed(self):
        """Message field 'nunchuk_joystick_zeroed'."""
        return self._nunchuk_joystick_zeroed

    @nunchuk_joystick_zeroed.setter
    def nunchuk_joystick_zeroed(self, value):
        if self._check_fields:
            if isinstance(value, numpy.ndarray):
                assert value.dtype == numpy.float32, \
                    "The 'nunchuk_joystick_zeroed' numpy.ndarray() must have the dtype of 'numpy.float32'"
                assert value.size == 2, \
                    "The 'nunchuk_joystick_zeroed' numpy.ndarray() must have a size of 2"
                self._nunchuk_joystick_zeroed = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 2 and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'nunchuk_joystick_zeroed' field must be a set or sequence with length 2 and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._nunchuk_joystick_zeroed = numpy.array(value, dtype=numpy.float32)

    @builtins.property
    def nunchuk_joystick_raw(self):
        """Message field 'nunchuk_joystick_raw'."""
        return self._nunchuk_joystick_raw

    @nunchuk_joystick_raw.setter
    def nunchuk_joystick_raw(self, value):
        if self._check_fields:
            if isinstance(value, numpy.ndarray):
                assert value.dtype == numpy.float32, \
                    "The 'nunchuk_joystick_raw' numpy.ndarray() must have the dtype of 'numpy.float32'"
                assert value.size == 2, \
                    "The 'nunchuk_joystick_raw' numpy.ndarray() must have a size of 2"
                self._nunchuk_joystick_raw = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 2 and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'nunchuk_joystick_raw' field must be a set or sequence with length 2 and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._nunchuk_joystick_raw = numpy.array(value, dtype=numpy.float32)

    @builtins.property
    def buttons(self):
        """Message field 'buttons'."""
        return self._buttons

    @buttons.setter
    def buttons(self, value):
        if self._check_fields:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 11 and
                 all(isinstance(v, bool) for v in value) and
                 True), \
                "The 'buttons' field must be a set or sequence with length 11 and each value of type 'bool'"
        self._buttons = value

    @builtins.property
    def nunchuk_buttons(self):
        """Message field 'nunchuk_buttons'."""
        return self._nunchuk_buttons

    @nunchuk_buttons.setter
    def nunchuk_buttons(self, value):
        if self._check_fields:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 2 and
                 all(isinstance(v, bool) for v in value) and
                 True), \
                "The 'nunchuk_buttons' field must be a set or sequence with length 2 and each value of type 'bool'"
        self._nunchuk_buttons = value

    @builtins.property
    def leds(self):
        """Message field 'leds'."""
        return self._leds

    @leds.setter
    def leds(self, value):
        if self._check_fields:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 4 and
                 all(isinstance(v, bool) for v in value) and
                 True), \
                "The 'leds' field must be a set or sequence with length 4 and each value of type 'bool'"
        self._leds = value

    @builtins.property
    def rumble(self):
        """Message field 'rumble'."""
        return self._rumble

    @rumble.setter
    def rumble(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'rumble' field must be of type 'bool'"
        self._rumble = value

    @builtins.property
    def ir_tracking(self):
        """Message field 'ir_tracking'."""
        return self._ir_tracking

    @ir_tracking.setter
    def ir_tracking(self, value):
        if self._check_fields:
            from wiimote_msgs.msg import IrSourceInfo
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, IrSourceInfo) for v in value) and
                 True), \
                "The 'ir_tracking' field must be a set or sequence and each value of type 'IrSourceInfo'"
        self._ir_tracking = value

    @builtins.property
    def raw_battery(self):
        """Message field 'raw_battery'."""
        return self._raw_battery

    @raw_battery.setter
    def raw_battery(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'raw_battery' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'raw_battery' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._raw_battery = value

    @builtins.property
    def percent_battery(self):
        """Message field 'percent_battery'."""
        return self._percent_battery

    @percent_battery.setter
    def percent_battery(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'percent_battery' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'percent_battery' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._percent_battery = value

    @builtins.property
    def zeroing_time(self):
        """Message field 'zeroing_time'."""
        return self._zeroing_time

    @zeroing_time.setter
    def zeroing_time(self, value):
        if self._check_fields:
            from builtin_interfaces.msg import Time
            assert \
                isinstance(value, Time), \
                "The 'zeroing_time' field must be a sub message of type 'Time'"
        self._zeroing_time = value

    @builtins.property
    def errors(self):
        """Message field 'errors'."""
        return self._errors

    @errors.setter
    def errors(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'errors' field must be of type 'int'"
            assert value >= 0 and value < 18446744073709551616, \
                "The 'errors' field must be an unsigned integer in [0, 18446744073709551615]"
        self._errors = value
