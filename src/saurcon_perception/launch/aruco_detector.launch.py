from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

# Marker size, dictionary and camera intrinsics are read from the JSON files in
# config/ (marker_params.json, camera_params.json), not from launch parameters.

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'image_topic',
            default_value='/camera/image',
            description='Input image topic'
        ),
        DeclareLaunchArgument(
            'aruco_topic',
            default_value='/aruco_poses',
            description='Output topic for detected marker poses'
        ),

        Node(
            package='saurcon_perception',
            executable='aruco_detector',
            name='aruco_detector',
            output='screen',
            parameters=[{
                'camera_topic': LaunchConfiguration('image_topic'),
                'aruco_topic': LaunchConfiguration('aruco_topic'),
            }],
        ),
    ])
