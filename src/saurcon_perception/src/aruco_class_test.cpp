#include "aruco_detector.hpp"
#include "Eigen/Dense"

#include <iostream>

int main(){
    std::cout << "====== ARUCO Class Test ======" << std::endl;

    std::string camera_json = "config/camera_params.json";
    std::string marker_json = "config/marker_params.json";
    auto detector = aruco_detector(camera_json, marker_json);

    //Let's load in an image
    cv::Mat img = cv::imread("/home/wilson-desktop/saurcon_ws/src/saurcon_perception/data/test_images/frame_000001_1771129137.042909.png");

    auto tags = detector.getTagsInImage(img);

    for(auto i : tags){
        std::cout << "[ Marker ID : " << i.tag_id << " ] tvec | " << i.tag_pose(0,3) << " " << i.tag_pose(1,3) << " " << i.tag_pose(2,3) << std::endl;
    }
    
    return 0;
}
