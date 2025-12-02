import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from datetime import datetime

def generate_launch_description():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create bags directory if it doesn't exist
    bags_dir = os.path.expanduser('~/saurcon_ws/bags')
    os.makedirs(bags_dir, exist_ok=True)
    
    bag_path = os.path.join(bags_dir, f"rosbag_{timestamp}")
    
    return LaunchDescription([
        # Launch the basement world in gz sim
        ExecuteProcess(
            cmd=[
                'gz', 'sim',
                '/home/wilson/saurcon_ws/src/middle_earth/worlds/basement.world'
            ],
            output='screen'
        ),
        
        # gz-ros-bridge node - using separate processes to avoid argument concatenation
        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                '/model/rc_ackermann_vehicle/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            ],
            output='screen',
            shell=False
        ),
        
        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                '/model/rc_ackermann_vehicle/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            ],
            output='screen',
            shell=False
        ),
        
        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                '/model/rc_ackermann_vehicle/imu@sensor_msgs/msg/Imu@gz.msgs.IMU',
            ],
            output='screen',
            shell=False
        ),
        
        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                '/camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            ],
            output='screen',
            shell=False
        ),
        
        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                '/camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            ],
            output='screen',
            shell=False
        ),
        
        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                '/model/rc_ackermann_vehicle/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            ],
            output='screen',
            shell=False
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
                'ros2', 'bag', 'record', '-a',
                '-o', bag_path
            ],
            output='screen'
        ),
    ])