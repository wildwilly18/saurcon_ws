import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction
from datetime import datetime

def find_workspace_root():
    """Find workspace root by searching for src/middle_earth directory."""
    # Start from the launch file's location
    current = os.path.dirname(os.path.abspath(__file__))
    
    # Search up the directory tree
    for _ in range(10):  # Limit search depth
        potential_ws = current
        # Check if this looks like a workspace (has src/middle_earth)
        if os.path.isdir(os.path.join(potential_ws, 'src', 'middle_earth')):
            return potential_ws
        # Also check if we're inside install/ and workspace is parent
        parent = os.path.dirname(current)
        if os.path.basename(current) == 'install' or os.path.isdir(os.path.join(parent, 'src', 'middle_earth')):
            if os.path.isdir(os.path.join(parent, 'src', 'middle_earth')):
                return parent
        current = parent
    
    raise RuntimeError("Could not find workspace root containing src/middle_earth")

def generate_launch_description():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get workspace path by finding src/middle_earth
    ws_path = find_workspace_root()
    
    # Create bags directory if it doesn't exist
    bags_dir = os.path.join(ws_path, 'bags')
    os.makedirs(bags_dir, exist_ok=True)
    
    bag_path = os.path.join(bags_dir, f"rosbag_{timestamp}")
    
    # World file path
    #world_path = os.path.join(ws_path, 'src/middle_earth/worlds/basement.world')
    world_path = os.path.join(ws_path, 'src/middle_earth/worlds/racetrack.world')
    
    # Resource paths for Gazebo (models and materials)
    middle_earth_path = os.path.join(ws_path, 'src/middle_earth')
    models_path = os.path.join(middle_earth_path, 'models')
    gz_resource_path = f"{models_path}:{middle_earth_path}"
    
    # Merge with existing GZ_SIM_RESOURCE_PATH if set
    existing_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    if existing_path:
        gz_resource_path = f"{gz_resource_path}:{existing_path}"
    
    return LaunchDescription([
        # Launch the basement world in gz sim
        ExecuteProcess(
            cmd=[
                'gz', 'sim', '-r',
                world_path
            ],
            output='screen',
            additional_env={'GZ_SIM_RESOURCE_PATH': gz_resource_path}
        ),
        
        # Delay bridge nodes to give Gazebo time to start
        TimerAction(period=5.0, actions=[
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

        ]),
        
        # Static transforms: base_link = rear_axle_center
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_camera_tf',
            arguments=['0.219', '0', '0.05', '0', '0', '0', 'base_link', 'camera_link']
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_imu_tf',
            arguments=['0.125', '0', '0', '0', '0', '0', 'base_link', 'imu_link']
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
        
        # aruco_detector node with necessary parameters and remappings
        Node(
            package='saurcon_perception',
            executable='aruco_detector',
            name='aruco_detector',
            output='screen',
            parameters=[{
                'marker_size': 0.1524,
                'dictionary_id': 4,  # DICT_4X4_50
                'camera_frame': 'camera_link',
                'publish_visualization': True,
                'min_marker_id': 0,
                'max_marker_id': 19,
            }],
            remappings=[
                ('image_raw', '/camera/image'),
                ('camera_info', '/camera/camera_info'),
            ]
        ),

        # aruco_loclizer node with necessary parameters and remappings
        Node(
            package='saurcon_perception',
            executable='aruco_localizer',
            name='aruco_localizer',
            output='screen',
            parameters=[{
                'marker_size': 0.1524,
                'camera_frame': 'camera_link',
                'publish_visualization': True,
            }],
            remappings=[
                ('image_raw', '/camera/image'),
                ('camera_info', '/camera/camera_info'),
                ('odom', '/model/rc_ackermann_vehicle/odom'),
            ]
        ),

        # state_estimator node
        Node(
            package='saurcon_nav',
            executable='state_estimator_node',
            name='state_estimator',
            output='both'
        ),
        
        # rosbag record all topics (mcap for Foxglove Studio compatibility)
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record', '-a',
                '--storage', 'mcap',
                '-o', bag_path
            ],
            output='screen'
        ),
    ])