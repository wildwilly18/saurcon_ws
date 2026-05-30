#include "rclcpp/rclcpp.hpp"
#include "state_estimator.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"

#include <cmath>
#include <chrono>

class StateEstimatorNode : public rclcpp::Node
{
public:
    StateEstimatorNode() : Node("StateEstimator")
    {
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/saurcon/imu", 10,
            std::bind(&StateEstimatorNode::imu_cb, this, std::placeholders::_1));

        odom_sub_ = this->create_subscription<geometry_msgs::msg::TwistStamped>(
            "/saurcon/odom", 10,
            std::bind(&StateEstimatorNode::odom_cb, this, std::placeholders::_1));

        aruco_sub_ = this->create_subscription<geometry_msgs::msg::PoseWithCovarianceStamped>(
            "/saurcon/aruco_localization", 10,
            std::bind(&StateEstimatorNode::aruco_cb, this, std::placeholders::_1));

        // 50 Hz spin timer
        constexpr double spin_hz = 50.0;
        dt_ = 1.0 / spin_hz;
        spin_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(static_cast<int>(1000.0 / spin_hz)),
            std::bind(&StateEstimatorNode::spin_cb, this));

        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>(
            "/saurcon/nav_state", 10);
    }

private:
    void imu_cb(const sensor_msgs::msg::Imu::SharedPtr msg){
        saurcon_nav::IMU_t imu;
        imu.time_stamp = msg->header.stamp.sec + msg->header.stamp.nanosec * 1e-9;
        imu.accel(0)   = msg->linear_acceleration.x;
        imu.accel(1)   = msg->linear_acceleration.y;
        imu.accel(2)   = msg->linear_acceleration.z;
        imu.w_b(0)     = msg->angular_velocity.x;
        imu.w_b(1)     = msg->angular_velocity.y;
        imu.w_b(2)     = msg->angular_velocity.z;
        engine_.add_measure(imu);
    }

    void odom_cb(const geometry_msgs::msg::TwistStamped::SharedPtr msg){
        saurcon_nav::ODOM_t odom;
        odom.time_stamp = msg->header.stamp.sec + msg->header.stamp.nanosec * 1e-9;
        odom.v_b        = msg->twist.linear.x;
        engine_.add_measure(odom);
    }

    void aruco_cb(const geometry_msgs::msg::PoseWithCovarianceStamped::SharedPtr msg){
        saurcon_nav::Aruco_loc_t loc;
        loc.time_stamp = msg->header.stamp.sec + msg->header.stamp.nanosec * 1e-9;
        loc.x          = msg->pose.pose.position.x;
        loc.y          = msg->pose.pose.position.y;

        // Extract yaw from quaternion
        const auto& q = msg->pose.pose.orientation;
        loc.theta = std::atan2(2.0*(q.w*q.z + q.x*q.y),
                               1.0 - 2.0*(q.y*q.y + q.z*q.z));

        // 6×6 covariance row-major: xx=[0], yy=[7], yaw-yaw=[35]
        loc.var_x     = msg->pose.covariance[0];
        loc.var_y     = msg->pose.covariance[7];
        loc.var_theta = msg->pose.covariance[35];

        engine_.add_measure(loc);
    }

    void spin_cb(){
        engine_.spin(dt_);

        nav_msgs::msg::Odometry msg;
        msg.header.stamp    = this->now();
        msg.header.frame_id = "odom";
        msg.child_frame_id  = "base_link";

        const auto& X = engine_.getX();
        const auto& P = engine_.getP();

        msg.pose.pose.position.x = X(saurcon_nav::STATE_IDX::X);
        msg.pose.pose.position.y = X(saurcon_nav::STATE_IDX::Y);
        msg.pose.pose.position.z = 0.0;

        double yaw = X(saurcon_nav::STATE_IDX::Theta);
        msg.pose.pose.orientation.x = 0.0;
        msg.pose.pose.orientation.y = 0.0;
        msg.pose.pose.orientation.z = std::sin(yaw * 0.5);
        msg.pose.pose.orientation.w = std::cos(yaw * 0.5);

        msg.twist.twist.linear.x = X(saurcon_nav::STATE_IDX::V);

        // Fill 6x6 pose covariance (row-major) from P_k_p_ [X,Y,Theta,V]
        msg.pose.covariance[0]  = P(saurcon_nav::STATE_IDX::X,     saurcon_nav::STATE_IDX::X);
        msg.pose.covariance[7]  = P(saurcon_nav::STATE_IDX::Y,     saurcon_nav::STATE_IDX::Y);
        msg.pose.covariance[35] = P(saurcon_nav::STATE_IDX::Theta, saurcon_nav::STATE_IDX::Theta);

        odom_pub_->publish(msg);
    }

    saurcon_nav::StateEstimator engine_;
    double dt_{0.02};

    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr                           imu_sub_;
    rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr                odom_sub_;
    rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr   aruco_sub_;
    rclcpp::TimerBase::SharedPtr                                                     spin_timer_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr                            odom_pub_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<StateEstimatorNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

