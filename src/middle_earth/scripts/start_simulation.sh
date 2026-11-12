#!/bin/bash

# Start the basement world in Gazebo together with the ROS 2 bridge.
# Requires a sourced ROS 2 environment (source /opt/ros/jazzy/setup.bash).

SIM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SIM_DIR"
export GZ_SIM_RESOURCE_PATH="$SIM_DIR/models:$SIM_DIR${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"

GZ_PID=""
BRIDGE_PID=""

# Stop only the processes this script started.
cleanup() {
    trap - EXIT INT TERM
    echo ""
    echo "Stopping simulation..."
    [ -n "$BRIDGE_PID" ] && kill "$BRIDGE_PID" 2>/dev/null
    [ -n "$GZ_PID" ] && kill "$GZ_PID" 2>/dev/null
    wait 2>/dev/null
    echo "Done."
}
trap cleanup EXIT INT TERM

echo "Starting Gazebo simulation..."
gz sim -r worlds/basement.world &
GZ_PID=$!
echo "Gazebo started (PID: $GZ_PID)"

# Wait for Gazebo to initialize
sleep 5

echo "Starting ROS 2 <-> Gazebo bridge..."
ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:="$SIM_DIR/config/bridge_config.yaml" &
BRIDGE_PID=$!
echo "Bridge started (PID: $BRIDGE_PID)"

echo ""
echo "Simulation running!"
echo ""
echo "Available ROS 2 topics:"
sleep 2
ros2 topic list | grep -E "(cmd_vel|imu|camera|odom|joint_states)"
echo ""
echo "To control the vehicle:"
echo "  python3 $SIM_DIR/scripts/teleop_vehicle.py"
echo "or"
echo "  ros2 topic pub /model/rc_ackermann_vehicle/cmd_vel geometry_msgs/msg/Twist \"{linear: {x: 0.5}, angular: {z: 0.0}}\""
echo ""
echo "Press Ctrl+C to stop (stops both Gazebo and the bridge)"

# Keep script running
wait
