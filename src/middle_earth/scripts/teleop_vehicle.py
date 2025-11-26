#!/usr/bin/env python3
"""
Simple teleoperation script for RC Ackermann vehicle
Use keyboard to control the vehicle:
  w/s: forward/backward
  a/d: steer left/right
  space: stop
  q: quit
"""

import sys
import tty
import termios
import rospy
from geometry_msgs.msg import Twist

class TeleopVehicle:
    def __init__(self):
        rospy.init_node('teleop_vehicle')
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        
        # Vehicle parameters
        self.max_linear_speed = 1.0   # m/s
        self.max_angular_speed = 0.5  # rad/s
        self.linear_increment = 0.1
        self.angular_increment = 0.1
        
        # Current velocities
        self.linear_vel = 0.0
        self.angular_vel = 0.0
        
        # Key bindings
        self.key_bindings = {
            'w': (1, 0),    # forward
            's': (-1, 0),   # backward
            'a': (0, 1),    # left
            'd': (0, -1),   # right
            ' ': (0, 0),    # stop
        }
        
    def get_key(self):
        """Get a single keypress from the terminal."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def print_status(self):
        """Print current velocity status."""
        print(f"\rLinear: {self.linear_vel:.2f} m/s | Angular: {self.angular_vel:.2f} rad/s", end='')
        sys.stdout.flush()
    
    def run(self):
        """Main teleoperation loop."""
        print("\n" + "="*60)
        print("RC Ackermann Vehicle Teleoperation")
        print("="*60)
        print("Controls:")
        print("  w/s : Forward/Backward")
        print("  a/d : Steer Left/Right")
        print("  Space : Stop")
        print("  q : Quit")
        print("="*60 + "\n")
        
        rate = rospy.Rate(10)  # 10 Hz
        
        try:
            while not rospy.is_shutdown():
                key = self.get_key()
                
                if key == 'q':
                    print("\nQuitting...")
                    break
                
                if key in self.key_bindings:
                    linear_dir, angular_dir = self.key_bindings[key]
                    
                    if key == ' ':
                        # Stop
                        self.linear_vel = 0.0
                        self.angular_vel = 0.0
                    else:
                        # Update velocities
                        if linear_dir != 0:
                            self.linear_vel = linear_dir * self.max_linear_speed
                        if angular_dir != 0:
                            self.angular_vel = angular_dir * self.max_angular_speed
                    
                    # Publish twist message
                    twist = Twist()
                    twist.linear.x = self.linear_vel
                    twist.angular.z = self.angular_vel
                    self.pub.publish(twist)
                    
                    self.print_status()
                
                rate.sleep()
                
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            # Send stop command
            twist = Twist()
            self.pub.publish(twist)
            print("\nStopped vehicle.")

if __name__ == '__main__':
    try:
        teleop = TeleopVehicle()
        teleop.run()
    except rospy.ROSInterruptException:
        pass
