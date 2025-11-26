import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from datetime import datetime

def generate_launch_description():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bag_name = f"rosbag_{timestamp}"

    return LaunchDescription([
        # Launch the basement world in gz sim
        ExecuteProcess(
            cmd=[
                'gz', 'sim',
                '/home/wilson/saurcon_ws/src/middle_earth/worlds/basement.world'
            ],
            output='screen'
        ),

            # gz-ros-bridge node
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                name='gz_bridge',
                output='screen',
                    arguments=[
                        # Velocity control (publish to this topic)
                        '/model/rc_ackermann_vehicle/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                        # Odometry (subscribe to this topic)
                        '/model/rc_ackermann_vehicle/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                        # Camera color image (subscribe to this topic)
                        '/camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
                        # Camera depth image (subscribe to this topic)
                        '/camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
                    ]
            ),
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

        # sim_rc mode
        Node(
            package='control_rc',
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