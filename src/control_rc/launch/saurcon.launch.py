import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory, get_package_prefix

def generate_launch_description():
    # Dynamically get the full path to the micro_ros_agent binary
    agent_prefix = get_package_prefix('micro_ros_agent')
    agent_executable = os.path.join(agent_prefix, 'lib', 'micro_ros_agent', 'micro_ros_agent')

    return LaunchDescription([
        # joy_node
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='log'
        ),

        # state_machine node
        Node(
            package='control_rc',
            executable='saurcon_main',
            name='saurcon_agent',
            output='both'
        ),

        # micro_ros_agent with dynamic path
        ExecuteProcess(
            cmd=[
                agent_executable, 'serial',
                '--dev', '/dev/ttyUSB0',
                '--baudrate', '921600'
            ],
            name='micro_ros_agent',
            output='both'
        )
    ])
