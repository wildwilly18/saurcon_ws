from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    def tf(parent, child, xyz=(0, 0, 0), rpy=(0, 0, 0)):
        return Node(package='tf2_ros', executable='static_transform_publisher',
                    name=child + '_tf', parameters=[{'use_sim_time': True}],
                    arguments=['--frame-id', parent, '--child-frame-id', child,
                               '--x', str(xyz[0]), '--y', str(xyz[1]), '--z', str(xyz[2]),
                               '--roll', str(rpy[0]), '--pitch', str(rpy[1]), '--yaw', str(rpy[2])])
    nodes = [tf('base_link', 'oak', (.219, 0, .05)), tf('oak', 'oak_imu_frame'),
             tf('oak_rgb_camera_frame', 'camera_link'),
             tf('oak_rgb_camera_optical_frame', 'camera_optical_frame')]
    for name, y in [('rgb', 0), ('left', .0375), ('right', -.0375)]:
        nodes += [tf('oak', f'oak_{name}_camera_frame', (0, y, 0)),
                  tf(f'oak_{name}_camera_frame', f'oak_{name}_camera_optical_frame',
                     rpy=(-1.5707963267948966, 0, -1.5707963267948966))]
    nodes.append(Node(package='saurcon_nav', executable='oak_depth.py',
                      parameters=[{'use_sim_time': True}], output='screen'))
    return LaunchDescription(nodes)
