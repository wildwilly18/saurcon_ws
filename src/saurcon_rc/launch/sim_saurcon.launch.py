import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from datetime import datetime

def generate_launch_description():
    # Timestamped bag name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bag_name = f"rosbag_{timestamp}"

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
            package='saurcon_rc',
            executable='saurcon_main',
            name='saurcon_agent',
            output='both'
        ),

        # sim_rc mode
        Node(
            package='saurcon_rc',
            executable='sim_saurcon_rc',
            name='sim_saurcon_rc',
            output='both'
        ),

        # rosbag record all topics
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-a'
            ],
            output='screen'
        ),
    ])
