#include "control_rc/topic_bridge.hpp"

using std::placeholders::_1;

IMUBridge::IMUBridge(rclcpp::Node* node) : node_(node) {
    // Best-effort QoS for micro-ROS subscription
    rclcpp::QoS micro_qos(
        rclcpp::QoSInitialization::from_rmw(rmw_qos_profile_sensor_data)
    );
    micro_qos.best_effort();
    micro_qos.durability_volatile();

    // Default reliable QoS for rqt/tools
    rclcpp::QoS default_qos(10);

    // Subscribe to micro-ROS published topic
    imu_sub_ = node_->create_subscription<sensor_msgs::msg::Imu>(
        "/imu/data_raw",  // Absolute topic
        micro_qos,
        std::bind(&IMUBridge::imu_callback, this, _1)
    );

    // Republish as reliable for rqt/rviz
    imu_pub_ = node_->create_publisher<sensor_msgs::msg::Imu>(
        "/bridge/imu_data",
        default_qos
    );

    RCLCPP_INFO(node_->get_logger(), "[IMUBridge] Subscribed to /imu/data_raw, publishing to /bridge/imu_data");

    // Optional: force test message to verify pub shows up in topic list
    /*
    sensor_msgs::msg::Imu test_msg;
    test_msg.header.stamp = node_->now();
    test_msg.header.frame_id = "imu_link";
    imu_pub_->publish(test_msg);
    RCLCPP_INFO(node_->get_logger(), "[IMUBridge] Published test IMU message to /bridge/imu_data");
    */
}

void IMUBridge::imu_callback(const sensor_msgs::msg::Imu::SharedPtr msg) {
    RCLCPP_DEBUG(node_->get_logger(), "[IMUBridge] Received IMU message, republishing...");
    imu_pub_->publish(*msg);
}
