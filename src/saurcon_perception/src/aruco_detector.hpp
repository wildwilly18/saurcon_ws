#pragma once

#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>
#include <Eigen/Dense>
#include <vector>
#include <map>
#include <string>

struct ArucoPose_t{
    int             tag_id;
    cv::Matx44d     tag_pose;
};

//Some helper functions here that allow us to build up our xForm matrices
inline cv::Matx44d makeT(const cv::Matx33d R, const cv::Vec3d& t){
    cv::Matx44d T = cv::Matx44d::eye();
    for(int r=0; r<3; ++r)
        for(int c=0; c<3; ++c)
            T(r,c) = R(r,c);
    
    T(0,3) = t[0];
    T(1,3) = t[1];
    T(2,3) = t[2];

    return T;
}

inline cv::Matx33d rodriguesToMatx33d(const cv::Vec3d& rvec){
    cv::Mat Rcv;
    cv::Rodrigues(cv::Mat(rvec), Rcv);
    cv::Matx33d R;
    Rcv.convertTo(R, CV_64F);
    return R;
}

class aruco_detector
{
public:
    aruco_detector(const std::string& camera_params_path, const std::string& marker_params_path);
    ~aruco_detector();

    std::vector<ArucoPose_t> getTagsInImage(cv::Mat& image);

private:
    void loadCameraParams(const std::string& filepath);
    void loadMarkerParams(const std::string& filepath);
    cv::Mat makeCameraMatrixForImage(const cv::Mat& image) const;

    // Camera intrinsics
    cv::Mat camMatrix_;
    cv::Mat distCoeffs_;
    double horizontal_fov_rad_ = 0.0;
    int configured_image_width_ = 0;
    int configured_image_height_ = 0;
    
    // Camera transform (from camera_params.json)
    cv::Vec3d cam_translation_;
    cv::Vec3d cam_rotation_;  // roll, pitch, yaw

    cv::Matx44d T_vc_ = cv::Matx44d::zeros();
    
    // Marker parameters
    cv::aruco::PREDEFINED_DICTIONARY_NAME dictionary_name_;
    double marker_length_;
};

