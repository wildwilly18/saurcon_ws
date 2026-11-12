#include "rclcpp/rclcpp.hpp"
#include "state_estimator.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "geometry_msgs/msg/pose_with_covariance_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "nav_msgs/msg/path.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"

#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <chrono>
#include <string>

namespace {
// Planar pose helpers: (x, y, yaw).
struct Pose2 { double x{0}, y{0}, th{0}; };
double yawOf(const geometry_msgs::msg::Quaternion& q){
    return std::atan2(2.0*(q.w*q.z + q.x*q.y), 1.0 - 2.0*(q.y*q.y + q.z*q.z));
}
Pose2 compose(const Pose2& a, const Pose2& b){            // a ⊕ b
    const double c = std::cos(a.th), s = std::sin(a.th);
    return {a.x + c*b.x - s*b.y, a.y + s*b.x + c*b.y, a.th + b.th};
}
Pose2 inverse(const Pose2& a){
    const double c = std::cos(a.th), s = std::sin(a.th);
    return {-c*a.x - s*a.y, s*a.x - c*a.y, -a.th};
}
Pose2 fromTf(const geometry_msgs::msg::TransformStamped& t){
    return {t.transform.translation.x, t.transform.translation.y, yawOf(t.transform.rotation)};
}
}

class StateEstimatorNode : public rclcpp::Node
{
public:
    // Modes (set by parameters):
    //  - ArUco (default): fuse /saurcon/aruco_localization, publish TF map -> base_link.
    //  - Odometry (use_aruco:=false): wheel + gyro only, publish TF odom -> base_link.
    //  - Global (fuse_localization:=true, tf_mode:=map_to_odom): fuse a map-frame pose
    //    such as RTAB-Map's /rtabmap/localization_pose on top of a separate odometry
    //    instance, and publish TF map -> odom so map -> odom -> base_link is the fused pose.
    StateEstimatorNode() : Node("StateEstimator"),
        engine_(declareFuse())
    {
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/saurcon/imu", 10,
            std::bind(&StateEstimatorNode::imu_cb, this, std::placeholders::_1));

        odom_sub_ = this->create_subscription<geometry_msgs::msg::TwistStamped>(
            "/saurcon/odom", 10,
            std::bind(&StateEstimatorNode::odom_cb, this, std::placeholders::_1));

        use_aruco_ = fuse_;
        const std::string loc_topic = this->declare_parameter<std::string>(
            "localization_topic", "/saurcon/aruco_localization");
        const std::string nav_topic = this->declare_parameter<std::string>(
            "nav_state_topic", "/saurcon/nav_state");
        std::string tf_mode = this->declare_parameter<std::string>("tf_mode", "auto");
        if (tf_mode == "auto") tf_mode = fuse_ ? "map_to_base" : "odom_to_base";
        if (tf_mode != "map_to_base" && tf_mode != "odom_to_base" && tf_mode != "map_to_odom")
            throw std::invalid_argument("tf_mode must be auto, map_to_base, odom_to_base or map_to_odom");
        if (tf_mode == "map_to_odom" && !fuse_)
            throw std::invalid_argument("tf_mode map_to_odom requires fuse_localization:=true");
        map_to_odom_ = (tf_mode == "map_to_odom");
        // Floors on the measurement noise of fused poses (RTAB-Map can report
        // near-zero covariance, which would make the filter jump to every fix).
        min_loc_pos_std_ = this->declare_parameter<double>("min_localization_position_std", 0.0);
        min_loc_yaw_std_ = this->declare_parameter<double>("min_localization_yaw_std", 0.0);
        if (map_to_odom_) {
            tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
            tf_listener_ = std::make_unique<tf2_ros::TransformListener>(*tf_buffer_);
        }
        if (fuse_ && !loc_topic.empty()) aruco_sub_ = this->create_subscription<geometry_msgs::msg::PoseWithCovarianceStamped>(
            loc_topic, 10,
            std::bind(&StateEstimatorNode::aruco_cb, this, std::placeholders::_1));
        // Alternative source: the newest pose of an optimized path. RTAB-Map publishes
        // /rtabmap/localization_pose only in localization mode; while mapping, the last
        // pose of /rtabmap/mapPath is its current corrected pose. No covariance is
        // given, so the min_localization_*_std floors set the measurement noise.
        const std::string path_topic = this->declare_parameter<std::string>("localization_path_topic", "");
        if (fuse_ && !path_topic.empty()) path_sub_ = this->create_subscription<nav_msgs::msg::Path>(
            path_topic, 10,
            std::bind(&StateEstimatorNode::path_cb, this, std::placeholders::_1));

        // 50 Hz spin timer
        constexpr double spin_hz = 50.0;
        dt_ = 1.0 / spin_hz;
        spin_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(static_cast<int>(1000.0 / spin_hz)),
            std::bind(&StateEstimatorNode::spin_cb, this));

        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>(nav_topic, 10);
        if (!use_aruco_) odom_nav_pub_ = this->create_publisher<nav_msgs::msg::Odometry>(
            "/saurcon/odom_nav", 10);

        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    }

private:
    bool declareFuse(){
        const bool aruco = this->declare_parameter<bool>("use_aruco", true);
        fuse_ = this->declare_parameter<bool>("fuse_localization", aruco);
        return fuse_;
    }

    void path_cb(const nav_msgs::msg::Path::SharedPtr msg){
        if (msg->poses.empty()) return;
        const auto& last = msg->poses.back();
        const rclcpp::Time stamp(last.header.stamp.sec || last.header.stamp.nanosec
                                 ? last.header.stamp : msg->header.stamp);
        if (have_last_path_ && stamp <= last_path_stamp_) return;   // no new node
        last_path_stamp_ = stamp; have_last_path_ = true;
        auto fix = std::make_shared<geometry_msgs::msg::PoseWithCovarianceStamped>();
        fix->header.frame_id = msg->header.frame_id;
        fix->header.stamp = stamp;
        fix->pose.pose = last.pose;
        aruco_cb(fix);
    }

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

        // The fix describes the car when its camera frame was taken, typically a few
        // hundred ms ago. Shift it to the present with the odometry travelled since.
        Pose2 fix{loc.x, loc.y, yawOf(msg->pose.pose.orientation)};
        if (map_to_odom_) {
            try {
                const Pose2 then = fromTf(tf_buffer_->lookupTransform(
                    "odom", "base_link", rclcpp::Time(msg->header.stamp)));
                const Pose2 now = fromTf(tf_buffer_->lookupTransform(
                    "odom", "base_link", tf2::TimePointZero));
                fix = compose(fix, compose(inverse(then), now));
                loc.time_stamp = rclcpp::Time(tf_buffer_->lookupTransform(
                    "odom", "base_link", tf2::TimePointZero).header.stamp).seconds();
            } catch (const tf2::TransformException& e) {
                RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                    "Using localization fix without latency compensation: %s", e.what());
            }
            loc.x = fix.x; loc.y = fix.y;
        }

        // Extract yaw from quaternion
        const auto& q = msg->pose.pose.orientation;
        loc.theta = std::atan2(2.0*(q.w*q.z + q.x*q.y),
                               1.0 - 2.0*(q.y*q.y + q.z*q.z));

        // 6×6 covariance row-major: xx=[0], yy=[7], yaw-yaw=[35]
        loc.var_x     = std::max(msg->pose.covariance[0],  min_loc_pos_std_ * min_loc_pos_std_);
        loc.var_y     = std::max(msg->pose.covariance[7],  min_loc_pos_std_ * min_loc_pos_std_);
        loc.var_theta = std::max(msg->pose.covariance[35], min_loc_yaw_std_ * min_loc_yaw_std_);
        if (map_to_odom_) loc.theta = std::atan2(std::sin(fix.th), std::cos(fix.th));

        engine_.add_measure(loc);
    }

    void spin_cb(){
        // Step the filter by the time that actually elapsed on the node clock
        // (simulation time when use_sim_time is set), not by the nominal period.
        const rclcpp::Time now = this->now();
        double dt = dt_;
        if (have_last_spin_) {
            dt = (now - last_spin_time_).seconds();
            if (dt < 0.0) dt = 0.0;          // clock jumped back (sim reset)
            if (dt > kMaxDt) dt = kMaxDt;    // long stall: do not extrapolate far
        }
        last_spin_time_ = now;
        have_last_spin_ = true;

        engine_.spin(dt);

        // Only publish once the filter has a pose; before that the state is all zeros.
        if (engine_.getCurrentState() != saurcon_nav::SaurconNavState::NAVIGATE) {
            return;
        }

        nav_msgs::msg::Odometry msg;
        msg.header.stamp    = now;
        msg.header.frame_id = fuse_ ? "map" : "odom";
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
        msg.twist.covariance[0] = P(saurcon_nav::STATE_IDX::V,     saurcon_nav::STATE_IDX::V);
        const int pose_indices[] = {0, 1, 5};
        for (int i = 0; i < 3; ++i)
            for (int j = 0; j < 3; ++j)
                msg.pose.covariance[6 * pose_indices[i] + pose_indices[j]] = P(i, j);
        // The planar vehicle model constrains z/roll/pitch. RTAB-Map takes
        // the maximum rotational variance: marking these as unbounded would
        // incorrectly discard our measured yaw constraint in graph optimization.
        for (int i : {2, 3, 4}) msg.pose.covariance[7 * i] = 1e-4;
        for (int i = 1; i < 6; ++i) msg.twist.covariance[7 * i] = 1e-4;
        msg.twist.twist.angular.z = engine_.getYawRate();
        msg.twist.covariance[35] = 0.009 * 0.009;  // simulated car IMU sample noise

        odom_pub_->publish(msg);
        if (odom_nav_pub_) odom_nav_pub_->publish(msg);

        geometry_msgs::msg::TransformStamped tf;
        tf.header = msg.header;
        tf.child_frame_id = msg.child_frame_id;
        tf.transform.translation.x = msg.pose.pose.position.x;
        tf.transform.translation.y = msg.pose.pose.position.y;
        tf.transform.translation.z = 0.0;
        tf.transform.rotation = msg.pose.pose.orientation;
        if (map_to_odom_) {
            // map -> odom = (map -> base_link) ⊕ (odom -> base_link)^-1
            try {
                const auto ob = tf_buffer_->lookupTransform("odom", "base_link", tf2::TimePointZero);
                const Pose2 mo = compose(Pose2{msg.pose.pose.position.x, msg.pose.pose.position.y, yaw},
                                         inverse(fromTf(ob)));
                tf.header.frame_id = "map";
                tf.child_frame_id = "odom";
                tf.transform.translation.x = mo.x;
                tf.transform.translation.y = mo.y;
                tf.transform.rotation.z = std::sin(mo.th * 0.5);
                tf.transform.rotation.w = std::cos(mo.th * 0.5);
                tf_broadcaster_->sendTransform(tf);
            } catch (const tf2::TransformException& e) {
                RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                    "map -> odom not published (no odom -> base_link yet): %s", e.what());
            }
            return;
        }
        tf_broadcaster_->sendTransform(tf);
    }

    // Declared before engine_: engine_'s initializer (declareFuse) sets it, and a
    // member declared later would be re-initialized after that, discarding the value.
    bool fuse_{false};
    saurcon_nav::StateEstimator engine_;
    bool use_aruco_{true};
    bool map_to_odom_{false};
    double min_loc_pos_std_{0.0};
    double min_loc_yaw_std_{0.0};
    std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
    std::unique_ptr<tf2_ros::TransformListener> tf_listener_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_nav_pub_;
    double dt_{0.02};
    static constexpr double kMaxDt = 0.2;
    rclcpp::Time last_spin_time_;
    bool have_last_spin_{false};
    std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr                           imu_sub_;
    rclcpp::Subscription<geometry_msgs::msg::TwistStamped>::SharedPtr                odom_sub_;
    rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr   aruco_sub_;
    rclcpp::Subscription<nav_msgs::msg::Path>::SharedPtr                             path_sub_;
    rclcpp::Time last_path_stamp_;
    bool have_last_path_{false};
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

