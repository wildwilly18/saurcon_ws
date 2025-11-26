#!/bin/bash

# Start Gazebo simulation and ROS 2 bridge together

echo "Starting Gazebo simulation..."
cd /home/wilson/saurcon_sim/middle_earth

# Kill any existing processes
killall -9 gz 2>/dev/null
pkill -9 gz 2>/dev/null
pkill -f ros_gz_bridge 2>/dev/null
sleep 1

# Start Gazebo in background
gz sim worlds/basement.world &
GZ_PID=$!
echo "Gazebo started (PID: $GZ_PID)"

# Wait for Gazebo to initialize
sleep 5

# Start ROS 2 bridge
echo "Starting ROS 2 <-> Gazebo bridge..."
ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:=/home/wilson/saurcon_ws/src/middle_earth/config/bridge_config.yaml &
BRIDGE_PID=$!
echo "Bridge started (PID: $BRIDGE_PID)"

echo ""
echo "Simulation running!"
echo "Gazebo PID: $GZ_PID"
echo "Bridge PID: $BRIDGE_PID"
echo ""
echo "Available ROS 2 topics:"
sleep 2
ros2 topic list | grep -E "(cmd_vel|imu|camera)"
echo ""
echo "To control the vehicle:"
echo "  ros2 topic pub /cmd_vel geometry_msgs/Twist \"{linear: {x: 0.5}, angular: {z: 0.0}}\""
echo ""
echo "Press Ctrl+C to stop (kills both Gazebo and bridge)"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping simulation..."
    kill $GZ_PID 2>/dev/null
    kill $BRIDGE_PID 2>/dev/null
    killall -9 gz 2>/dev/null
    pkill -f ros_gz_bridge 2>/dev/null
    echo "Done."
}

trap cleanup EXIT INT TERM

# Keep script running
wait
