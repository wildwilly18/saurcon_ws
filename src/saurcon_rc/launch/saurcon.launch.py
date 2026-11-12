import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from datetime import datetime
from ament_index_python.packages import get_package_prefix


def bag_output_path():
    """Timestamped bag path under $SAURCON_BAG_DIR (default: ~/saurcon_bags)."""
    bags_dir = os.environ.get('SAURCON_BAG_DIR',
                              os.path.join(os.path.expanduser('~'), 'saurcon_bags'))
    os.makedirs(bags_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(bags_dir, f"rosbag_{timestamp}")


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

        # state_machine node
        Node(
            package='saurcon_rc',
            executable='saurcon_main',
            name='saurcon_agent',
            output='both'
        ),

        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-a',  # record all topics
                '-o', bag_output_path()
            ],
            output='screen'
        ),

        # micro_ros_agent with dynamic path
        ExecuteProcess(
            cmd=[
                agent_executable, 'serial',
                '--dev', LaunchConfiguration('serial_dev'),
                '--baudrate', LaunchConfiguration('baudrate')
            ],
            shell=True,
            name='micro_ros_agent',
            output='both'
        ),
    ])
