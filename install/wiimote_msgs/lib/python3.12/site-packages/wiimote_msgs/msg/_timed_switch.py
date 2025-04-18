# generated from rosidl_generator_py/resource/_idl.py.em
# with input from wiimote_msgs:msg/TimedSwitch.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

# Member 'pulse_pattern'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_TimedSwitch(type):
    """Metaclass of message 'TimedSwitch'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'ON': 1,
        'OFF': 0,
        'NO_CHANGE': -2,
        'REPEAT': -1,
        'FOREVER': -1,
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
                'wiimote_msgs.msg.TimedSwitch')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__timed_switch
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__timed_switch
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__timed_switch
            cls._TYPE_SUPPORT = module.type_support_msg__msg__timed_switch
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__timed_switch

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'ON': cls.__constants['ON'],
            'OFF': cls.__constants['OFF'],
            'NO_CHANGE': cls.__constants['NO_CHANGE'],
            'REPEAT': cls.__constants['REPEAT'],
            'FOREVER': cls.__constants['FOREVER'],
        }

    @property
    def ON(self):
        """Message constant 'ON'."""
        return Metaclass_TimedSwitch.__constants['ON']

    @property
    def OFF(self):
        """Message constant 'OFF'."""
        return Metaclass_TimedSwitch.__constants['OFF']

    @property
    def NO_CHANGE(self):
        """Message constant 'NO_CHANGE'."""
        return Metaclass_TimedSwitch.__constants['NO_CHANGE']

    @property
    def REPEAT(self):
        """Message constant 'REPEAT'."""
        return Metaclass_TimedSwitch.__constants['REPEAT']

    @property
    def FOREVER(self):
        """Message constant 'FOREVER'."""
        return Metaclass_TimedSwitch.__constants['FOREVER']


class TimedSwitch(metaclass=Metaclass_TimedSwitch):
    """
    Message class 'TimedSwitch'.

    Constants:
      ON
      OFF
      NO_CHANGE
      REPEAT
      FOREVER
    """

    __slots__ = [
        '_switch_mode',
        '_num_cycles',
        '_pulse_pattern',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'switch_mode': 'int8',
        'num_cycles': 'int32',
        'pulse_pattern': 'sequence<float>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
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
        self.switch_mode = kwargs.get('switch_mode', int())
        self.num_cycles = kwargs.get('num_cycles', int())
        self.pulse_pattern = array.array('f', kwargs.get('pulse_pattern', []))

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
        if self.switch_mode != other.switch_mode:
            return False
        if self.num_cycles != other.num_cycles:
            return False
        if self.pulse_pattern != other.pulse_pattern:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def switch_mode(self):
        """Message field 'switch_mode'."""
        return self._switch_mode

    @switch_mode.setter
    def switch_mode(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'switch_mode' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'switch_mode' field must be an integer in [-128, 127]"
        self._switch_mode = value

    @builtins.property
    def num_cycles(self):
        """Message field 'num_cycles'."""
        return self._num_cycles

    @num_cycles.setter
    def num_cycles(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'num_cycles' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'num_cycles' field must be an integer in [-2147483648, 2147483647]"
        self._num_cycles = value

    @builtins.property
    def pulse_pattern(self):
        """Message field 'pulse_pattern'."""
        return self._pulse_pattern

    @pulse_pattern.setter
    def pulse_pattern(self, value):
        if self._check_fields:
            if isinstance(value, array.array):
                assert value.typecode == 'f', \
                    "The 'pulse_pattern' array.array() must have the type code of 'f'"
                self._pulse_pattern = value
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
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'pulse_pattern' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._pulse_pattern = array.array('f', value)
