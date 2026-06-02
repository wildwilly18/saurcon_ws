#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.hpp>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2/LinearMath/Quaternion.h>
#include <saurcon_perception/msg/aruco_pose_array.hpp>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <fstream>
#include <sstream>
#include <unordered_set>
#include <unordered_map>
#include "aruco_detector.hpp"

class ArucoDetectorNode : public rclcpp::Node{
public:
    ArucoDetectorNode() : Node("aruco_detector"){
        //Declaration of parameters
        this->declare_parameter("camera_topic", "/camera/image");
        this->declare_parameter("aruco_topic", "/aruco_poses");
        this->declare_parameter("camera_frame_id", "camera_optical_frame");
        this->declare_parameter("enable_whitelist_filter", true);
        this->declare_parameter("consecutive_frames_required", 2);

        std::string camera_topic = this->get_parameter("camera_topic").as_string();
        std::string aruco_topic  = this->get_parameter("aruco_topic").as_string();
        camera_frame_id_ = this->get_parameter("camera_frame_id").as_string();
        enable_whitelist_filter_ = this->get_parameter("enable_whitelist_filter").as_bool();
        consecutive_frames_required_ = this->get_parameter("consecutive_frames_required").as_int();
        if (consecutive_frames_required_ < 1) {
            consecutive_frames_required_ = 1;
        }

        // Get package share directory for config files
        std::string package_share_dir = ament_index_cpp::get_package_share_directory("saurcon_perception");
        std::string camera_json = package_share_dir + "/config/camera_params.json";
        std::string marker_json = package_share_dir + "/config/marker_params.json";
        std::string marker_map_csv = package_share_dir + "/config/marker_map.csv";

        // Initialize the aruco detector
        aruco_detector_ = std::make_unique<aruco_detector>(camera_json, marker_json);
        loadWhitelistFromCsv(marker_map_csv);

        //Create the subscriber for the camera images
        image_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            camera_topic, 10,
            std::bind(&ArucoDetectorNode::imageCallback, this, std::placeholders::_1));

        aruco_pub_ = this->create_publisher<saurcon_perception::msg::ArucoPoseArray>(
            aruco_topic, 10);

        RCLCPP_INFO(this->get_logger(), "ArUco Detector Node initialized");
        RCLCPP_INFO(this->get_logger(), "Subscribing to: %s", camera_topic.c_str());
        RCLCPP_INFO(this->get_logger(), "Publishing to: %s", aruco_topic.c_str());
        RCLCPP_INFO(this->get_logger(), "Whitelist filter: %s (%zu IDs loaded)",
                    enable_whitelist_filter_ ? "enabled" : "disabled", whitelist_ids_.size());
        RCLCPP_INFO(this->get_logger(), "Consecutive frames required: %d", consecutive_frames_required_);
    }

private:
    std::string camera_frame_id_;
    bool enable_whitelist_filter_{true};
    int consecutive_frames_required_{2};
    std::unordered_set<int> whitelist_ids_;
    std::unordered_set<int> previous_frame_ids_;
    std::unordered_map<int, int> consecutive_hits_;

    void loadWhitelistFromCsv(const std::string& filepath){
        std::ifstream file(filepath);
        if (!file.is_open()) {
            RCLCPP_WARN(this->get_logger(), "Could not open marker map CSV for whitelist: %s", filepath.c_str());
            return;
        }

        std::string line;
        while (std::getline(file, line)) {
            if (line.empty() || line[0] == '#') {
                continue;
            }

            std::istringstream ss(line);
            std::string token;
            if (!std::getline(ss, token, ',')) {
                continue;
            }

            if (token == "id") {
                continue;
            }

            try {
                whitelist_ids_.insert(std::stoi(token));
            } catch (const std::exception&) {
                // Ignore malformed rows.
            }
        }
    }

    void imageCallback(const sensor_msgs::msg::Image::SharedPtr msg){
        //Convert ROS image to opencv format
        cv_bridge::CvImagePtr cv_ptr;
        try{
            cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
        } catch (cv_bridge::Exception& e){
            RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
            return;
        }

        // Detect ArUco markers
        auto detections = aruco_detector_->getTagsInImage(cv_ptr->image);

        //Create the ArUcoPoseArray message set frame ID to the camera frame id
        saurcon_perception::msg::ArucoPoseArray pose_array;
        pose_array.header.stamp = msg->header.stamp;
        pose_array.header.frame_id = msg->header.frame_id;

        // Process each detected marker
        std::unordered_set<int> current_frame_ids;
        std::unordered_map<int, int> next_consecutive_hits;

        for(const auto& detection : detections){
            const int tag_id = detection.tag_id;

            if (enable_whitelist_filter_ && !whitelist_ids_.empty() && whitelist_ids_.count(tag_id) == 0) {
                continue;
            }

            if (current_frame_ids.count(tag_id) > 0) {
                continue;
            }

            current_frame_ids.insert(tag_id);

            int hits = 1;
            if (previous_frame_ids_.count(tag_id) > 0) {
                auto it = consecutive_hits_.find(tag_id);
                if (it != consecutive_hits_.end()) {
                    hits = it->second + 1;
                } else {
                    hits = 2;
                }
            }
            next_consecutive_hits[tag_id] = hits;

            if (hits < consecutive_frames_required_) {
                continue;
            }

            saurcon_perception::msg::ArucoPose aruco_pose;
            aruco_pose.tag_id = tag_id;

            //Set Pose Header
            aruco_pose.pose.header.stamp = msg->header.stamp;
            aruco_pose.pose.header.frame_id = msg->header.frame_id;

            //Extract translation from the 4x4 matrix, 4th column
            aruco_pose.pose.pose.position.x = detection.tag_pose(0,3);
            aruco_pose.pose.pose.position.y = detection.tag_pose(1,3);
            aruco_pose.pose.pose.position.z = detection.tag_pose(2,3);

            //Extract the rotation matrix and convert it to a quaternion
            tf2::Matrix3x3 rotation_matrix(
                detection.tag_pose(0, 0), detection.tag_pose(0, 1), detection.tag_pose(0, 2),
                detection.tag_pose(1, 0), detection.tag_pose(1, 1), detection.tag_pose(1, 2),
                detection.tag_pose(2, 0), detection.tag_pose(2, 1), detection.tag_pose(2, 2)
            );

            tf2::Quaternion quaternion;
            rotation_matrix.getRotation(quaternion);

            aruco_pose.pose.pose.orientation.x = quaternion.x();
            aruco_pose.pose.pose.orientation.y = quaternion.y();
            aruco_pose.pose.pose.orientation.z = quaternion.z();
            aruco_pose.pose.pose.orientation.w = quaternion.w();

            pose_array.poses.push_back(aruco_pose);
        }

        previous_frame_ids_ = std::move(current_frame_ids);
        consecutive_hits_ = std::move(next_consecutive_hits);

        //Publish the poses
        aruco_pub_->publish(pose_array);
    }

    std::unique_ptr<aruco_detector> aruco_detector_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_sub_;
    rclcpp::Publisher<saurcon_perception::msg::ArucoPoseArray>::SharedPtr aruco_pub_;
};

int main(int argc, char** argv){
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ArucoDetectorNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}