"""RTAB-Map only; full_sim_saurcon launches the vehicle and wheel odometry."""
import os
from pathlib import Path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    mode = LaunchConfiguration('mode').perform(context)
    if mode not in ('mapping', 'localization'):
        raise ValueError('mode must be mapping or localization')
    database = Path(LaunchConfiguration('database_path').perform(context)).expanduser().resolve()
    visual = LaunchConfiguration('visual_odometry').perform(context).lower() == 'true'
    reset = LaunchConfiguration('reset_database').perform(context).lower() == 'true'
    initial_pose = LaunchConfiguration('initial_pose', default='').perform(context).strip()
    # When saurcon_nav's global UKF fuses RTAB-Map's pose (full_sim fuse_slam:=true),
    # that filter owns map -> odom; RTAB-Map must not publish it as well.
    fused = (LaunchConfiguration('fuse_slam', default='false').perform(context).lower() == 'true'
             and not visual)
    if initial_pose and (mode != 'localization' or len(initial_pose.split()) != 6):
        raise ValueError('initial_pose is "x y z roll pitch yaw" in the map frame, localization mode only')
    if mode == 'localization' and (reset or not database.is_file()):
        raise ValueError('Localization requires an existing database and reset_database:=false')
    database.parent.mkdir(parents=True, exist_ok=True)
    image_remaps = [('rgb/image', '/oak/rgb/image_raw'),
                    ('depth/image', '/oak/stereo/image_raw'),
                    ('rgb/camera_info', '/oak/rgb/camera_info')]
    nodes = []
    if visual:
        nodes.append(Node(package='rtabmap_odom', executable='rgbd_odometry',
                          name='visual_odometry', output='screen',
                          parameters=[{'use_sim_time': True, 'frame_id': 'base_link',
                                       'odom_frame_id': 'odom', 'publish_tf': True,
                                       'approx_sync': True, 'Reg/Force3DoF': 'true'}],
                          remappings=image_remaps + [('odom', '/saurcon/nav_state')]))
    nodes.append(Node(package='rtabmap_slam', executable='rtabmap', namespace='rtabmap',
        name='rtabmap', output='screen', arguments=['--delete_db_on_start'] if reset else [],
        parameters=[{
            'use_sim_time': True, 'frame_id': 'base_link', 'map_frame_id': 'map',
            # Odometry comes from TF (odom -> base_link) with a fixed variance per link
            # between map nodes. The wheel/gyro filter's own covariance is the total
            # accumulated since start-up; RTAB-Map treats odometry covariance as the
            # uncertainty of each link, so passing it through made long runs look
            # metres-uncertain and let false loop closures in repetitive aisles pass
            # RGBD/OptimizeMaxError. Values: 5 mm and 0.18 deg (1 sigma) per node.
            # Measured sim drift is about 0.15 m over 420 nodes (~7 mm per node as a
            # random walk). The variance must be tight enough that a false closure
            # between look-alike aisles (a 4 m jump spread over ~160 links) exceeds
            # 3 sigma per link; 2 cm per link let it through. Re-measure on hardware.
            'odom_frame_id': 'odom',
            'odom_tf_linear_variance': 2.5e-5, 'odom_tf_angular_variance': 1e-5,
            'subscribe_depth': True, 'approx_sync': True,
            'approx_sync_max_interval': .05, 'topic_queue_size': 30, 'sync_queue_size': 30,
            'database_path': str(database), 'publish_tf': not fused,
            'Reg/Force3DoF': 'true', 'Optimizer/Strategy': '1', 'RGBD/NeighborLinkRefining': 'false',
            'RGBD/OptimizeMaxError': '3.0', 'Rtabmap/DetectionRate': '2.0',
            'Grid/FromDepth': 'true', 'Grid/RangeMax': '4.0', 'Grid/CellSize': '0.05',
            'Grid/MaxGroundHeight': '0.03', 'Grid/MaxObstacleHeight': '1.5',
            'Vis/MinInliers': '20',
            'Mem/IncrementalMemory': 'true' if mode == 'mapping' else 'false',
            'Mem/InitWMWithAllNodes': 'false' if mode == 'mapping' else 'true',
            # Known start pose (e.g. parked where it was last shut down, or set by an
            # operator). Without it RTAB-Map must relocalize globally, which can lock
            # onto a look-alike place while the car is stationary.
            **({'initial_pose': initial_pose} if initial_pose else {}),
        }], remappings=image_remaps + [('odom', '/saurcon/nav_state' if visual else '/saurcon/odom_nav'), ('map', '/map')]))
    return nodes


def generate_launch_description():
    ws = os.environ.get('SAURCON_WS', str(Path.cwd()))
    return LaunchDescription([
        DeclareLaunchArgument('visual_odometry', default_value='false'),
        DeclareLaunchArgument('mode', default_value='mapping'),
        DeclareLaunchArgument('database_path', default_value=os.path.join(ws, 'maps', 'rtabmap.db')),
        DeclareLaunchArgument('reset_database', default_value='false'),
        DeclareLaunchArgument('initial_pose', default_value='',
                              description='"x y z roll pitch yaw" in the map frame (localization only)'),
        OpaqueFunction(function=setup)])
