import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from datetime import datetime
from ament_index_python.packages import get_package_share_directory, get_package_prefix

def generate_launch_description():
    # Dynamically get the full path to the micro_ros_agent binary
    agent_prefix = get_package_prefix('micro_ros_agent')
    agent_executable = os.path.join(agent_prefix, 'lib', 'micro_ros_agent', 'micro_ros_agent')

    # Timestamped bag name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bag_name = f"rosbag_{timestamp}"

    return LaunchDescription([
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
                '-a'  # record all topics
            ],
            output='screen'
        ),

        # micro_ros_agent with dynamic path
        ExecuteProcess(
            cmd=[
                agent_executable, 'serial',
                '--dev', '/dev/ttyUSB0',
                '--baudrate', '921600'
            ],
            shell=True,
            name='micro_ros_agent',
            output='both'
        ),


    ])
