import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_prefix

# Minimal bring-up: the joystick drives /ctrl_output directly through
# ctrl_interface, with no state machine in between. Do not run this together
# with saurcon.launch.py / saurcon_main, which also publishes /ctrl_output.

def generate_launch_description():
    # Dynamically get the full path to the micro_ros_agent binary
    agent_prefix = get_package_prefix('micro_ros_agent')
    agent_executable = os.path.join(agent_prefix, 'lib', 'micro_ros_agent', 'micro_ros_agent')

    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_dev', default_value='/dev/ttyUSB0',
            description='Serial device the ESP32 (micro-ROS client) is attached to'
        ),
        DeclareLaunchArgument(
            'baudrate', default_value='921600',
            description='Serial baud rate for the micro-ROS agent'
        ),

        # joy_node
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen'
        ),

        # ctrl_interface node
        Node(
            package='saurcon_rc',
            executable='ctrl_interface',
            name='ctrl_interface',
            output='screen'
        ),

        # micro_ros_agent with dynamic path
        ExecuteProcess(
            cmd=[
                agent_executable, 'serial',
                '--dev', LaunchConfiguration('serial_dev'),
                '--baudrate', LaunchConfiguration('baudrate')
            ],
            name='micro_ros_agent',
            output='screen'
        )
    ])
