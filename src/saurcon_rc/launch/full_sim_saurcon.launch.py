import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from datetime import datetime


def find_workspace_root():
    """Locate the workspace that contains src/middle_earth.

    The simulation assets (worlds, models, bridge config) live in the source
    tree rather than in an installed package. Set SAURCON_WS to point at the
    workspace explicitly; otherwise search upwards from this launch file.
    """
    env_ws = os.environ.get('SAURCON_WS')
    if env_ws:
        if os.path.isdir(os.path.join(env_ws, 'src', 'middle_earth')):
            return env_ws
        raise RuntimeError(
            f"SAURCON_WS={env_ws} does not contain src/middle_earth")

    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):  # Limit search depth
        if os.path.isdir(os.path.join(current, 'src', 'middle_earth')):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    raise RuntimeError(
        "Could not find the workspace root containing src/middle_earth. "
        "Set the SAURCON_WS environment variable to the workspace path.")


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

    bridge_config = os.path.join(middle_earth_path, 'config', 'bridge_config.yaml')

    # Nodes that process simulated sensor data run on the simulation clock
    # (/clock is bridged from Gazebo) so all their timestamps share one time base.
    sim_time = {'use_sim_time': True}

    return LaunchDescription([
        # Launch the world in gz sim
        ExecuteProcess(
            cmd=[
                'gz', 'sim', '-r',
                world_path
            ],
            output='screen',
            additional_env={'GZ_SIM_RESOURCE_PATH': gz_resource_path}
        ),

        # One ROS 2 <-> Gazebo bridge for every topic in bridge_config.yaml
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            output='screen',
            parameters=[{'config_file': bridge_config}],
        ),

        # Static transforms: base_link = rear_axle_center
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_camera_tf',
            arguments=['--x', '0.219', '--y', '0', '--z', '0.05',
                       '--yaw', '0', '--pitch', '0', '--roll', '0',
                       '--frame-id', 'base_link', '--child-frame-id', 'camera_link'],
            parameters=[sim_time],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_imu_tf',
            arguments=['--x', '0.125', '--y', '0', '--z', '0',
                       '--yaw', '0', '--pitch', '0', '--roll', '0',
                       '--frame-id', 'base_link', '--child-frame-id', 'imu_link'],
            parameters=[sim_time],
        ),

        # joy_node
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='log'
        ),

        # state_machine node (wall clock: its joystick/RC watchdogs must keep
        # running even if the simulation is paused)
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
            output='both',
            parameters=[sim_time],
        ),

        # aruco_detector node. Marker size, dictionary and camera intrinsics come
        # from saurcon_perception/config/*.json.
        Node(
            package='saurcon_perception',
            executable='aruco_detector',
            name='aruco_detector',
            output='screen',
            parameters=[sim_time, {
                'camera_topic': '/camera/image',
                'aruco_topic': '/aruco_poses',
            }],
        ),

        # aruco_localizer node
        Node(
            package='saurcon_perception',
            executable='aruco_localizer',
            name='aruco_localizer',
            output='screen',
            parameters=[sim_time, {
                'aruco_topic': '/aruco_poses',
                'localization_topic': '/saurcon/aruco_localization',
            }],
        ),

        # state_estimator node
        Node(
            package='saurcon_nav',
            executable='state_estimator_node',
            name='state_estimator',
            output='both',
            parameters=[sim_time],
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
