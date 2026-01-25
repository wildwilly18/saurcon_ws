#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.hpp>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2/LinearMath/Quaternion.h>
#include <saurcon_perception/msg/aruco_pose_array.hpp>
#include "aruco_detector.hpp"

class ArucoDetectorNode : public rclcpp::Node{
public:
    ArucoDetectorNode() : Node("aruco_detector_node"){
        //Declaration of parameters
        this->declare_parameter("camera_topic", "/camera/image_raw");
        this->declare_parameter("aruco_topic", "/aruco_poses");

        std::string camera_topic = this->get_parameter("camera_topic").as_string();
        std::string aruco_topic  = this->get_parameter("aruco_topic").as_string();

        std::string camera_json = "config/camera_params.json";
        std::string marker_json = "config/marker_params.json";

        // Initialize the aruco detector
        aruco_detector_ = std::make_unique<aruco_detector>(camera_json, marker_json);

        //Create the subscriber for the camera images
        image_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            camera_topic, 10,
            std::bind(&ArucoDetectorNode::imageCallback, this, std::placeholders::_1));

        aruco_pub_ = this->create_publisher<saurcon_perception::msg::ArucoPoseArray>(
            aruco_topic, 10);

        RCLCPP_INFO(this->get_logger(), "ArUco Detector Node initialized");
        RCLCPP_INFO(this->get_logger(), "Subscribing to: %s", camera_topic.c_str());
        RCLCPP_INFO(this->get_logger(), "Publishing to: %s", aruco_topic.c_str());
    }

private:
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

        if(detections.empty()){
            return; //no detections
        }

        //Create the ArUcoPoseArray message
        saurcon_perception::msg::ArucoPoseArray pose_array;
        pose_array.header.stamp = msg->header.stamp;
        pose_array.header.frame_id = msg->header.frame_id;

        // Process each detected marker
        for(const auto& detection : detections){
            saurcon_perception::msg::ArucoPose aruco_pose;
            aruco_pose.tag_id = detection.tag_id;

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

        //Publish the poses
        aruco_pub_->publish(pose_array);

        RCLCPP_DEBUG(this->get_logger(), "Published %zu ArUco poses", pose_array.poses.size());
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