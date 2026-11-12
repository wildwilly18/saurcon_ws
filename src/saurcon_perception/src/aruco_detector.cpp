#include "aruco_detector.hpp"

#include <iostream>
#include <fstream>
#include <sstream>
#include <cmath>
#include <boost/json.hpp>

namespace json = boost::json;

namespace {
// Pose-ambiguity rejection thresholds (see getTagsInImage).
constexpr double kAmbiguityAngleRad   = 15.0 * M_PI / 180.0;
constexpr double kAmbiguityErrorRatio = 2.0;
}

aruco_detector::aruco_detector(const std::string& camera_params_path, const std::string& marker_params_path)
{
    loadCameraParams(camera_params_path);
    loadMarkerParams(marker_params_path);

    // CLAHE-only preprocessing gave the most consistent startup detections in test.
    clahe_ = cv::createCLAHE(2.5, cv::Size(8, 8));

    // ArUco detection parameters tuned for sim imagery and startup tag visibility.
    // Inverted-marker detection stays off: with it on, the detector locks onto the
    // outer edge of the white plate instead of the marker border and misreads range.
    detector_params_ = cv::aruco::DetectorParameters::create();
    detector_params_->adaptiveThreshWinSizeMin  = 3;
    detector_params_->adaptiveThreshWinSizeMax  = 101;
    detector_params_->adaptiveThreshWinSizeStep = 4;
    detector_params_->adaptiveThreshConstant    = 7.0;
    // Ignore markers smaller than ~13 px per side (beyond roughly 4.5 m): their pose
    // is too noisy to be useful for localization.
    detector_params_->minMarkerPerimeterRate    = 0.08;
    // The marker square sits inside a white plate whose edge is only a few pixels
    // away. With the default (0.05) OpenCV treats the two quads as duplicates at
    // close range and keeps the plate, which then fails to decode.
    detector_params_->minMarkerDistanceRate     = 0.02;
    detector_params_->maxMarkerPerimeterRate    = 4.0;
    detector_params_->cornerRefinementMethod    = cv::aruco::CORNER_REFINE_SUBPIX;
    detector_params_->detectInvertedMarker      = false;

    dictionary_ = cv::aruco::getPredefinedDictionary(dictionary_name_);

    // Marker corners in the marker frame, in the order SOLVEPNP_IPPE_SQUARE requires:
    // top-left, top-right, bottom-right, bottom-left.
    const float h = static_cast<float>(marker_length_ / 2.0);
    obj_points_ = cv::Mat(4, 1, CV_32FC3);
    obj_points_.ptr<cv::Vec3f>(0)[0] = cv::Vec3f(-h,  h, 0);
    obj_points_.ptr<cv::Vec3f>(0)[1] = cv::Vec3f( h,  h, 0);
    obj_points_.ptr<cv::Vec3f>(0)[2] = cv::Vec3f( h, -h, 0);
    obj_points_.ptr<cv::Vec3f>(0)[3] = cv::Vec3f(-h, -h, 0);
}

aruco_detector::~aruco_detector()
{
}

std::vector<ArucoPose_t> aruco_detector::getTagsInImage(cv::Mat& image){
    std::vector<ArucoPose_t> tags;
    // Convert to grayscale if needed.
    cv::Mat gray;
    if(image.channels() > 1){
        cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
    } else {
        gray = image.clone();
    }

    cv::Mat clahe_image;
    clahe_->apply(gray, clahe_image);

    std::vector<int> markerIds;
    std::vector<std::vector<cv::Point2f>> markerCorners, rejectedCandidates;
    cv::aruco::detectMarkers(clahe_image, dictionary_, markerCorners, markerIds, detector_params_, rejectedCandidates);

    //If no markers found simply return
    if(markerIds.empty()){ return tags;}

    cv::Mat imageCamMatrix = makeCameraMatrixForImage(clahe_image);

    size_t nMarkers = markerCorners.size();

    // Estimate poses
    for(size_t i = 0; i < nMarkers; ++i){
        //std::cout << "Solving tag ID : " << markerIds.at(i) << std::endl;
        cv::Vec3d rvec;
        cv::Vec3d tvec;
        // IPPE_SQUARE is the solver intended for a single planar square marker. It
        // returns both candidate poses of the plane, best reprojection error first.
        std::vector<cv::Vec3d> rvecs, tvecs;
        std::vector<double> reproj_err;
        const int n_solutions = cv::solvePnPGeneric(
            obj_points_, markerCorners.at(i), imageCamMatrix, distCoeffs_, rvecs, tvecs,
            false, cv::SOLVEPNP_IPPE_SQUARE, cv::noArray(), cv::noArray(), reproj_err);
        if(n_solutions < 1){
            continue;
        }
        rvec = rvecs[0];
        tvec = tvecs[0];

        // A small or distant marker can be explained almost equally well by two
        // orientations mirrored about the line of sight. If the solver cannot tell
        // them apart and they disagree noticeably, the orientation (and therefore
        // the vehicle position derived from it) is unreliable: skip the detection.
        if(n_solutions > 1 && reproj_err.size() > 1){
            const cv::Matx33d R0 = rodriguesToMatx33d(rvecs[0]);
            const cv::Matx33d R1 = rodriguesToMatx33d(rvecs[1]);
            const double cos_angle = R0(0,2)*R1(0,2) + R0(1,2)*R1(1,2) + R0(2,2)*R1(2,2);
            const bool differ    = cos_angle < std::cos(kAmbiguityAngleRad);
            const bool ambiguous = reproj_err[1] < kAmbiguityErrorRatio * reproj_err[0] + 1e-6;
            if(differ && ambiguous){
                continue;
            }
        }

        //std::cout << "  Marker in camera frame: " << tvec << std::endl;

        cv::Matx33d R_cm = rodriguesToMatx33d(rvec);
        cv::Matx44d T_cm = makeT(R_cm, tvec);

        // Leave tag in the camera optical frame to be converted later
        ArucoPose_t marker_pose;
        marker_pose.tag_id = markerIds.at(i);
        marker_pose.tag_pose = T_cm;

        //std::cout<< "[ DEBUG ] Marker added to vector ID: " << marker_pose.tag_id << std::endl;
        tags.push_back(marker_pose);
    }

    return tags;
}

cv::Mat aruco_detector::makeCameraMatrixForImage(const cv::Mat& image) const
{
    cv::Mat imageCamMatrix = camMatrix_.clone();
    if (imageCamMatrix.empty()) {
        imageCamMatrix = cv::Mat::eye(3, 3, CV_64F);
    }

    if (horizontal_fov_rad_ > 0.0) {
        const double fx = static_cast<double>(image.cols) / (2.0 * std::tan(horizontal_fov_rad_ / 2.0));
        const double fy = fx;
        const double cx = static_cast<double>(image.cols) / 2.0;
        const double cy = static_cast<double>(image.rows) / 2.0;

        imageCamMatrix = (cv::Mat_<double>(3,3) <<
            fx, 0.0, cx,
            0.0, fy, cy,
            0.0, 0.0, 1.0);
    } else if (configured_image_width_ > 0 && configured_image_height_ > 0 && !camMatrix_.empty()) {
        const double sx = static_cast<double>(image.cols) / static_cast<double>(configured_image_width_);
        const double sy = static_cast<double>(image.rows) / static_cast<double>(configured_image_height_);

        imageCamMatrix = camMatrix_.clone();
        imageCamMatrix.at<double>(0,0) *= sx;
        imageCamMatrix.at<double>(1,1) *= sy;
        imageCamMatrix.at<double>(0,2) *= sx;
        imageCamMatrix.at<double>(1,2) *= sy;
    }

    return imageCamMatrix;
}

void aruco_detector::loadCameraParams(const std::string& filepath){
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open camera params file: " + filepath);
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    json::value j = json::parse(buffer.str());
    
    // Load image metadata and intrinsics from config.
    configured_image_width_ = static_cast<int>(j.at("camera").at("image").at("width").as_int64());
    configured_image_height_ = static_cast<int>(j.at("camera").at("image").at("height").as_int64());
    horizontal_fov_rad_ = j.at("camera").at("intrinsics").at("horizontal_fov").as_double();

    double fx = j.at("camera").at("intrinsics").at("focal_length_x").as_double();
    double fy = j.at("camera").at("intrinsics").at("focal_length_y").as_double();
    double cx = j.at("camera").at("intrinsics").at("principal_point_x").as_double();
    double cy = j.at("camera").at("intrinsics").at("principal_point_y").as_double();
    
    camMatrix_ = (cv::Mat_<double>(3,3) <<
        fx, 0.0, cx,
        0.0, fy, cy,
        0.0, 0.0, 1.0);
    
    // Distortion coefficients: optional "distortion" array [k1, k2, p1, p2, k3] in the
    // intrinsics block; zero (ideal pinhole, as in simulation) when absent.
    distCoeffs_ = cv::Mat::zeros(5, 1, CV_64F);
    const auto& intr = j.at("camera").at("intrinsics").as_object();
    if (intr.contains("distortion")) {
        const auto& d = intr.at("distortion").as_array();
        for (size_t i = 0; i < d.size() && i < 5; ++i) {
            distCoeffs_.at<double>(static_cast<int>(i), 0) = d[i].to_number<double>();
        }
    }

    // The camera mounting transform in this file is applied by aruco_localizer_node;
    // the detector reports marker poses in the camera optical frame.
    std::cout << "Loaded camera params from: " << filepath << std::endl;
    std::cout << "  Config image: " << configured_image_width_ << "x" << configured_image_height_ << std::endl;
    std::cout << "  Horizontal FOV: " << horizontal_fov_rad_ << " rad" << std::endl;
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