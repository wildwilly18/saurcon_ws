#!/bin/bash

# Start the ROS 2 <-> Gazebo bridge for the rc_ackermann_vehicle model.
# Requires a sourced ROS 2 environment (source /opt/ros/jazzy/setup.bash).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config/bridge_config.yaml"

echo "Starting ROS 2 <-> Gazebo bridge..."
echo "Config file: $CONFIG_FILE"
echo ""
echo "Bridged topics:"
grep -E '^- ros_topic_name' "$CONFIG_FILE" | sed -E 's/^- ros_topic_name: "(.*)"/  \1/'
echo ""

ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:="$CONFIG_FILE"
