import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch.actions import OpaqueFunction
from launch_ros.parameter_descriptions import ParameterValue
from datetime import datetime
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource


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


def check_mode(context):
    if LaunchConfiguration('visual_odometry').perform(context).lower() == 'true':
        if (LaunchConfiguration('slam').perform(context).lower() != 'true' or
                LaunchConfiguration('use_aruco').perform(context).lower() == 'true'):
            raise ValueError('Visual odometry requires slam:=true and use_aruco:=false')
    if (LaunchConfiguration('slam').perform(context).lower() == 'true' and
            LaunchConfiguration('use_aruco').perform(context).lower() == 'true'):
        raise ValueError('SLAM requires use_aruco:=false to avoid competing TF publishers')
    return []


def estimators(context, sim_time):
    """Wheel/gyro UKF instances.

    ArUco or odometry-only: one instance publishing /saurcon/nav_state.
    SLAM with fuse_slam (default): two instances.
      - state_estimator: odometry only, TF odom -> base_link, /saurcon/odom_nav and
        /saurcon/nav_state_odom. RTAB-Map uses this; it must never see RTAB-Map's
        own corrections, or the two would feed back into each other.
      - state_estimator_global: the same prediction plus RTAB-Map's pose as a
        measurement (/rtabmap/localization_pose when localizing, the newest
        /rtabmap/mapPath node when mapping). Publishes /saurcon/nav_state
        (map frame) and TF map -> odom.
    """
    truthy = lambda name: LaunchConfiguration(name).perform(context).lower() == 'true'
    if truthy('visual_odometry'):
        return []
    use_aruco = truthy('use_aruco')
    fuse = truthy('slam') and truthy('fuse_slam')
    nodes = [Node(
        package='saurcon_nav', executable='state_estimator_node', name='state_estimator',
        output='both',
        parameters=[sim_time, {'use_aruco': use_aruco,
                               'nav_state_topic': '/saurcon/nav_state_odom' if fuse else '/saurcon/nav_state'}])]
    if fuse:
        nodes.append(Node(
            package='saurcon_nav', executable='state_estimator_node', name='state_estimator_global',
            output='both',
            parameters=[sim_time, {
                'use_aruco': False, 'fuse_localization': True,
                # RTAB-Map's pose: localization mode publishes localization_pose;
                # mapping mode does not, so use the newest node of its optimized path.
                **({'localization_topic': '/rtabmap/localization_pose', 'localization_path_topic': ''}
                   if LaunchConfiguration('mode', default='mapping').perform(context) == 'localization'
                   else {'localization_topic': '', 'localization_path_topic': '/rtabmap/mapPath'}),
                'nav_state_topic': '/saurcon/nav_state', 'tf_mode': 'map_to_odom',
                'min_localization_position_std': 0.05, 'min_localization_yaw_std': 0.005}]))
    return nodes


RTAB_MAP_ORIGIN = '-1.127 0 0'      # world pose of the RTAB-Map frame: the rear axle at the racetrack spawn


def policy_map_origin(context):
    """World pose (x y yaw) of the frame /saurcon/nav_state is in, for the map-based racing policy.

    The policy needs a global pose. ArUco localization reports the pose in the world (marker map)
    frame: origin 0 0 0. RTAB-Map with fused SLAM reports it in the map frame, which starts where
    mapping started: `policy_map_origin` (default the racetrack spawn, RTAB_MAP_ORIGIN). Every other
    configuration publishes odometry on /saurcon/nav_state, which drifts and is not a map pose:
    rejected rather than silently used.
    """
    truthy = lambda name: LaunchConfiguration(name, default='false').perform(context).lower() == 'true'
    given = LaunchConfiguration('policy_map_origin', default='').perform(context).strip()
    if truthy('visual_odometry'):
        raise ValueError('policy_model needs a map pose; with visual_odometry:=true /saurcon/nav_state is '
                         'visual odometry. Use slam:=true fuse_slam:=true, or use_aruco:=true')
    if truthy('use_aruco'):
        if given and [float(v) for v in given.split()] != [0.0, 0.0, 0.0]:
            raise ValueError('use_aruco:=true reports world coordinates; policy_map_origin must be empty or "0 0 0"')
        return '0 0 0'
    if truthy('slam'):
        if not truthy('fuse_slam'):
            raise ValueError('policy_model with slam:=true needs fuse_slam:=true: without it /saurcon/nav_state '
                             'is wheel/gyro odometry, not the RTAB-Map pose')
        origin = given or RTAB_MAP_ORIGIN
        if len(origin.split()) != 3:
            raise ValueError(f'policy_map_origin is "x y yaw" (got "{origin}")')
        [float(v) for v in origin.split()]
        return origin
    raise ValueError('policy_model needs localization: use_aruco:=true, or slam:=true with fuse_slam:=true '
                     '(without either, /saurcon/nav_state is odometry only)')


def policy(context, ws_path):
    """RL racing policy node, run with the RL virtual environment's Python (needs torch)."""
    model = LaunchConfiguration('policy_model').perform(context)
    if not model:
        return []
    origin = policy_map_origin(context)
    python = os.path.join(ws_path, '.venv-rl', 'bin', 'python')
    if not os.path.exists(python):
        raise RuntimeError(f'{python} not found; run scripts/setup.sh to create the RL environment')
    return [ExecuteProcess(
        cmd=[python, '-m', 'saurcon_rl.policy_node', '--ros-args',
             '-p', 'use_sim_time:=true', '-p', f'model:={os.path.abspath(model)}',
             '-p', f"speed_limit:={LaunchConfiguration('policy_speed_limit').perform(context)}",
             '-p', f"map_origin:=[{', '.join(str(float(v)) for v in origin.split())}]",
             '-p', f"world:={LaunchConfiguration('world').perform(context)}"],
        name='race_policy', output='screen')]


def cone_policy(context, ws_path):
    model = LaunchConfiguration('cone_policy_model').perform(context)
    if not model:
        return []
    if LaunchConfiguration('policy_model', default='').perform(context):
        raise ValueError('Use either policy_model or cone_policy_model, not both (both publish /auto_cmd)')
    python = os.path.join(ws_path, '.venv-rl', 'bin', 'python')
    return [ExecuteProcess(
        cmd=[python, '-m', 'saurcon_rl.cone_policy_node', '--ros-args', '-p', 'use_sim_time:=true',
             '-p', f"model:={model if model == 'classical' else os.path.abspath(model)}",
             '-p', f"speed_limit:={LaunchConfiguration('policy_speed_limit', default='12.0').perform(context)}"]
            + (['-p', f'debug_csv:={dbg}'] if (dbg := LaunchConfiguration('cone_debug_csv', default='').perform(context))
               and model == 'classical' else []),
        name='cone_policy', output='screen')]


def cone_mappers(context):
    mode = LaunchConfiguration('cone_mapping').perform(context)
    if mode == 'none':
        return []
    sources = ['rtab', 'truth'] if mode == 'both' else [mode]
    out = LaunchConfiguration('cone_output_dir').perform(context)
    return [Node(package='saurcon_rl', executable='cone_mapper', name=f'cones_{src}', output='screen',
                 parameters=[{'use_sim_time': True, 'pose_source': src,
                              'world': LaunchConfiguration('world').perform(context),
                              'output_json': os.path.join(out, f'cones_{src}.json') if out else ''}])
            for src in sources]


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
    default_world = os.path.join(ws_path, 'src/middle_earth/worlds/racetrack.world')
    world_path = LaunchConfiguration('world')

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
        DeclareLaunchArgument("world", default_value=default_world),
        DeclareLaunchArgument("headless", default_value="false"),
        DeclareLaunchArgument("record", default_value="true"),
        DeclareLaunchArgument("use_aruco", default_value="true"),
        DeclareLaunchArgument("slam", default_value="false"),
        DeclareLaunchArgument("visual_odometry", default_value="false"),
        # With slam:=true, run a second UKF that fuses RTAB-Map's pose and owns map -> odom.
        DeclareLaunchArgument("fuse_slam", default_value="true"),
        # Path to a trained saurcon_rl policy (.zip). When set, the policy node drives
        # in RUN_AUTONOMOUS (hold view for 2 s in STANDBY).
        DeclareLaunchArgument("policy_model", default_value=""),
        DeclareLaunchArgument("policy_map_origin", default_value="",
                              description='World pose "x y yaw" of the RTAB-Map frame for policy_model '
                                          '(default: the racetrack spawn, -1.127 0 0; ArUco uses 0 0 0)'),
        # Cone detection + cone map: none | rtab | truth | both (truth needs /gt_pose,
        # published by scripts/sim_eval/gt_bridge.py). Scores go to cone_output_dir.
        DeclareLaunchArgument("cone_mapping", default_value="none"),
        # Path to a trained cone-vision policy (saurcon_rl.cone_env). Drives from the
        # camera alone; works with slam:=false (odometry only, no map).
        DeclareLaunchArgument("cone_policy_model", default_value=""),
        OpaqueFunction(function=cone_policy, kwargs={'ws_path': ws_path}),
        DeclareLaunchArgument("cone_output_dir", default_value=""),
        OpaqueFunction(function=cone_mappers),
        DeclareLaunchArgument("policy_speed_limit", default_value="12.0"),
        OpaqueFunction(function=policy, kwargs={'ws_path': ws_path}),
        OpaqueFunction(function=check_mode),
        ExecuteProcess(cmd=["gz", "sim", "-s", "-r", "--headless-rendering", world_path],
                       condition=IfCondition(LaunchConfiguration("headless")),
                       additional_env={"GZ_SIM_RESOURCE_PATH": gz_resource_path}, output="screen"),
        # Launch the world in gz sim
        ExecuteProcess(
            cmd=[
                'gz', 'sim', '-r',
                world_path
            ],
            condition=UnlessCondition(LaunchConfiguration('headless')),
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
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('saurcon_nav'), 'launch', 'oak_sim.launch.py'))),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('saurcon_nav'), 'launch', 'rtabmap_sim.launch.py')),
            condition=IfCondition(LaunchConfiguration('slam'))),
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
            condition=IfCondition(LaunchConfiguration('use_aruco')),
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
            condition=IfCondition(LaunchConfiguration('use_aruco')),
            output='screen',
            parameters=[sim_time, {
                'aruco_topic': '/aruco_poses',
                'localization_topic': '/saurcon/aruco_localization',
            }],
        ),

        # state_estimator node(s)
        OpaqueFunction(function=estimators, kwargs={'sim_time': sim_time}),

        # rosbag record all topics (mcap for Foxglove Studio compatibility)
        ExecuteProcess(
            condition=IfCondition(LaunchConfiguration('record')),
            cmd=[
                'ros2', 'bag', 'record', '-a',
                '--storage', 'mcap',
                '-o', bag_path
            ],
            output='screen'
        ),
    ])
