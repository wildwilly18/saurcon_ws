from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'marker_size',
            default_value='0.1524',
            description='Physical size of ArUco markers in meters'
        ),
        DeclareLaunchArgument(
            'camera_frame',
            default_value='camera_link',
            description='Frame ID for camera'
        ),
        DeclareLaunchArgument(
            'image_topic',
            default_value='/camera/image_raw',
            description='Input image topic'
        ),
        DeclareLaunchArgument(
            'camera_info_topic',
            default_value='/camera/camera_info',
            description='Camera info topic'
        ),
        
        Node(
            package='saurcon_perception',
            executable='aruco_detector_node',
            name='aruco_detector',
            output='screen',
            parameters=[{
                'marker_size': LaunchConfiguration('marker_size'),
                'dictionary_id': 4,  # DICT_4X4_50
                'camera_frame': LaunchConfiguration('camera_frame'),
                'publish_visualization': True,
                'min_marker_id': 0,
                'max_marker_id': 19,
            }],
            remappings=[
                ('image_raw', LaunchConfiguration('image_topic')),
                ('camera_info', LaunchConfiguration('camera_info_topic')),
            ]
        ),
    ])
