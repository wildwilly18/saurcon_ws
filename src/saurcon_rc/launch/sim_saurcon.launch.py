import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from datetime import datetime


def bag_output_path():
    """Timestamped bag path under $SAURCON_BAG_DIR (default: ~/saurcon_bags)."""
    bags_dir = os.environ.get('SAURCON_BAG_DIR',
                              os.path.join(os.path.expanduser('~'), 'saurcon_bags'))
    os.makedirs(bags_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(bags_dir, f"rosbag_{timestamp}")


def generate_launch_description():
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
                '-a',
                '-o', bag_output_path()
            ],
            output='screen'
        ),
    ])
