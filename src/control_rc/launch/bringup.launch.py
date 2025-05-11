from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        # joy_node from joy package
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen'
        ),

        # ctrl_interface node from control_rc package
        Node(
            package='control_rc',
            executable='ctrl_interface',
            name='ctrl_interface',
            output='screen'
        ),

        # micro_ros_agent as external process
        ExecuteProcess(
            cmd=[
                'micro_ros_agent', 'serial', '--dev', '/dev/ttyUSB0', '--baudrate', '921600'
            ],
            name='micro_ros_agent',
            output='screen'
        )
    ])
