#pragma once

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>

class IMUBridge {
public:
    explicit IMUBridge(rclcpp::Node* node);

private:
    void imu_callback(const sensor_msgs::msg::Imu::SharedPtr msg);

    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
    rclcpp::Node* node_;  // for logging
};