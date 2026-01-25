#include "aruco_detector.hpp"

#include <iostream>
#include <fstream>
#include <sstream>
#include <boost/json.hpp>

namespace json = boost::json;

aruco_detector::aruco_detector(const std::string& camera_params_path, const std::string& marker_params_path)
{
    loadCameraParams(camera_params_path);
    loadMarkerParams(marker_params_path);
}

aruco_detector::~aruco_detector()
{
}

std::vector<ArucoPose_t> aruco_detector::getTagsInImage(cv::Mat& image){
    std::vector<ArucoPose_t> tags;
    //check if image grayscale, if not convert
    if(image.channels() > 1){
        cv::cvtColor(image, image, cv::COLOR_BGR2GRAY);
    }

    //Apply threshold to image
    cv::threshold(image, image, 50, 255, cv::THRESH_BINARY);

     // Set up ArUco detection parameters
    std::vector<int> markerIds;
    std::vector<std::vector<cv::Point2f>> markerCorners, rejectedCandidates;
    cv::Ptr<cv::aruco::DetectorParameters> detectorParams = cv::aruco::DetectorParameters::create();

    // Use DICT_4X4_50 dictionary
    cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);
    
    // Detect markers using enhanced image (try both)
    cv::aruco::detectMarkers(image, dictionary, markerCorners, markerIds, detectorParams, rejectedCandidates);

    std::cout << "Detected " << markerIds.size() << " markers" << std::endl;

    //If no markers found simply return
    if(markerIds.empty()){ return tags;}

    //Maybe add in code here to draw to the original image?
    cv::Mat objPoints(4,1, CV_32FC3);
    objPoints.ptr<cv::Vec3f>(0)[0] = cv::Vec3f(-marker_length_/2.f, marker_length_/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[1] = cv::Vec3f(marker_length_/2.f, marker_length_/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[2] = cv::Vec3f(marker_length_/2.f, -marker_length_/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[3] = cv::Vec3f(-marker_length_/2.f, -marker_length_/2.f, 0);

    size_t nMarkers = markerCorners.size();

    // Estimate poses
    for(size_t i = 0; i < nMarkers; ++i){
        std::cout << "Solving tag ID : " << markerIds.at(i) << std::endl;
        cv::Vec3d rvec; cv::Vec3d tvec; 
        cv::solvePnP(objPoints, markerCorners.at(i), camMatrix_, distCoeffs_, rvec, tvec);

        std::cout << "  Marker in camera frame: " << tvec << std::endl;

        cv::Matx33d R_cm = rodriguesToMatx33d(rvec);
        cv::Matx44d T_cm = makeT(R_cm, tvec);

        cv::Matx44d T_vm = T_vc_ * T_cm;
        
        // Extract position from transformation matrix
        cv::Vec3d t_vm(T_vm(0,3), T_vm(1,3), T_vm(2,3));
        std::cout << "  Marker in vehicle frame: " << t_vm << std::endl;

        ArucoPose_t marker_pose;
        marker_pose.tag_id = markerIds.at(i);
        marker_pose.tag_pose = T_vm;

        std::cout<< "[ DEBUG ] Marker added to vector ID: " << marker_pose.tag_id << std::endl;        tags.push_back(marker_pose);
    }

    return tags;
}

void aruco_detector::loadCameraParams(const std::string& filepath){
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open camera params file: " + filepath);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    json::value j = json::parse(buffer.str());
    
    // Load intrinsics
    double fx = j.at("camera").at("intrinsics").at("focal_length_x").as_double();
    double fy = j.at("camera").at("intrinsics").at("focal_length_y").as_double();
    double cx = j.at("camera").at("intrinsics").at("principal_point_x").as_double();
    double cy = j.at("camera").at("intrinsics").at("principal_point_y").as_double();
    
    camMatrix_ = (cv::Mat_<double>(3,3) <<
        fx, 0.0, cx,
        0.0, fy, cy,
        0.0, 0.0, 1.0);
    
    // Initialize distortion coefficients (zero for simulation)
    distCoeffs_ = cv::Mat::zeros(5, 1, CV_64F);
    
    // Load transform
    cam_translation_[0] = j.at("transform").at("translation").at("x").as_double();
    cam_translation_[1] = j.at("transform").at("translation").at("y").as_double();
    cam_translation_[2] = j.at("transform").at("translation").at("z").as_double();
    
    cam_rotation_[0] = j.at("transform").at("rotation").at("roll").as_double();
    cam_rotation_[1] = j.at("transform").at("rotation").at("pitch").as_double();
    cam_rotation_[2] = j.at("transform").at("rotation").at("yaw").as_double();
    
    std::cout << "Loaded camera params from: " << filepath << std::endl;

    //Set up camera to vehicle xform
    // Camera frame: X=right, Y=down, Z=forward
    // Vehicle frame: X=forward, Y=left, Z=up
    // Transformation: Camera's Z → Vehicle's X, Camera's -X → Vehicle's Y, Camera's -Y → Vehicle's Z
    cv::Matx33d R_vc(
        0,  0,  1,   // Vehicle X = Camera Z (forward)
       -1,  0,  0,   // Vehicle Y = -Camera X (left)
        0, -1,  0    // Vehicle Z = -Camera Y (up)
    );
    cv::Vec3d   t_vc = cam_translation_;
    T_vc_ = makeT(R_vc, t_vc);
    
    std::cout << "Camera to Vehicle Transform:" << std::endl;
    std::cout << "  Translation: " << t_vc << std::endl;
    std::cout << "  Rotation matrix:" << std::endl;
    std::cout << "    " << R_vc << std::endl;
}

void aruco_detector::loadMarkerParams(const std::string& filepath)
{
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open marker params file: " + filepath);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    json::value j = json::parse(buffer.str());
    
    // Load marker length
    marker_length_ = j.at("marker").at("marker_length").as_double();
    
    // Load dictionary
    std::string dict_str = j.at("marker").at("dictionary").as_string().c_str();
    
    // Map string to enum
    static const std::map<std::string, cv::aruco::PREDEFINED_DICTIONARY_NAME> dict_map = {
        {"DICT_4X4_50", cv::aruco::DICT_4X4_50},
        {"DICT_4X4_100", cv::aruco::DICT_4X4_100},
        {"DICT_4X4_250", cv::aruco::DICT_4X4_250},
        {"DICT_4X4_1000", cv::aruco::DICT_4X4_1000},
        {"DICT_5X5_50", cv::aruco::DICT_5X5_50},
        {"DICT_5X5_100", cv::aruco::DICT_5X5_100},
        {"DICT_5X5_250", cv::aruco::DICT_5X5_250},
        {"DICT_5X5_1000", cv::aruco::DICT_5X5_1000},
        {"DICT_6X6_50", cv::aruco::DICT_6X6_50},
        {"DICT_6X6_100", cv::aruco::DICT_6X6_100},
        {"DICT_6X6_250", cv::aruco::DICT_6X6_250},
        {"DICT_6X6_1000", cv::aruco::DICT_6X6_1000},
        {"DICT_7X7_50", cv::aruco::DICT_7X7_50},
        {"DICT_7X7_100", cv::aruco::DICT_7X7_100},
        {"DICT_7X7_250", cv::aruco::DICT_7X7_250},
        {"DICT_7X7_1000", cv::aruco::DICT_7X7_1000},
        {"DICT_ARUCO_ORIGINAL", cv::aruco::DICT_ARUCO_ORIGINAL}
    };
    
    auto it = dict_map.find(dict_str);
    if (it != dict_map.end()) {
        dictionary_name_ = it->second;
    } else {
        throw std::runtime_error("Unknown dictionary name: " + dict_str);
    }
    
    std::cout << "Loaded marker params from: " << filepath << std::endl;
    std::cout << "  Dictionary: " << dict_str << std::endl;
    std::cout << "  Marker length: " << marker_length_ << "m" << std::endl;
}