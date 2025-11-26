#!/bin/bash

# Start ROS 2 <-> Gazebo Bridge
# This bridges topics between Gazebo and ROS 2

CONFIG_FILE="/home/wilson/saurcon_ws/src/middle_earth/config/bridge_config.yaml"

echo "Starting ROS 2 <-> Gazebo bridge..."
echo "Config file: $CONFIG_FILE"
echo ""
echo "Bridged topics:"
echo "  ROS 2 -> Gazebo:"
echo "    /cmd_vel (geometry_msgs/Twist)"
echo ""
echo "  Gazebo -> ROS 2:"
echo "    /imu (sensor_msgs/Imu)"
echo "    /camera/image (sensor_msgs/Image)"
echo "    /camera/depth (sensor_msgs/Image)"
echo "    /camera/points (sensor_msgs/PointCloud2)"
echo "    /camera/camera_info (sensor_msgs/CameraInfo)"
echo ""

ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:=$CONFIG_FILE
