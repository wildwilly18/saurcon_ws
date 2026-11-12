#!/usr/bin/env python3
"""
Simple keyboard teleoperation for the RC Ackermann vehicle (ROS 2).

  w/s   : forward / backward
  a/d   : steer left / right
  space : stop
  q     : quit

Publishes geometry_msgs/Twist on /model/rc_ackermann_vehicle/cmd_vel, which the
ROS 2 <-> Gazebo bridge forwards to the simulator. Pass a different topic as the
first argument if needed.
"""

import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist

DEFAULT_TOPIC = '/model/rc_ackermann_vehicle/cmd_vel'

MAX_LINEAR_SPEED = 1.0   # m/s
MAX_ANGULAR_SPEED = 0.5  # rad/s

# key -> (linear direction, angular direction)
KEY_BINDINGS = {
    'w': (1, 0),
    's': (-1, 0),
    'a': (0, 1),
    'd': (0, -1),
}


def get_key():
    """Read a single keypress from the terminal."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOPIC

    rclpy.init()
    node = rclpy.create_node('teleop_vehicle')
    pub = node.create_publisher(Twist, topic, 1)

    print('\n' + '=' * 60)
    print('RC Ackermann Vehicle Teleoperation')
    print('=' * 60)
    print(f'Publishing to: {topic}')
    print('  w/s   : Forward/Backward')
    print('  a/d   : Steer Left/Right')
    print('  Space : Stop')
    print('  q     : Quit')
    print('=' * 60 + '\n')

    linear_vel = 0.0
    angular_vel = 0.0

    try:
        while rclpy.ok():
            key = get_key()

            if key in ('q', '\x03'):  # q or Ctrl+C
                print('\nQuitting...')
                break

            if key == ' ':
                linear_vel = 0.0
                angular_vel = 0.0
            elif key in KEY_BINDINGS:
                linear_dir, angular_dir = KEY_BINDINGS[key]
                if linear_dir != 0:
                    linear_vel = linear_dir * MAX_LINEAR_SPEED
                if angular_dir != 0:
                    angular_vel = angular_dir * MAX_ANGULAR_SPEED
            else:
                continue

            twist = Twist()
            twist.linear.x = linear_vel
            twist.angular.z = angular_vel
            pub.publish(twist)

            print(f'\rLinear: {linear_vel:.2f} m/s | Angular: {angular_vel:.2f} rad/s   ', end='')
            sys.stdout.flush()
    finally:
        # Send stop command
        pub.publish(Twist())
        print('\nStopped vehicle.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
