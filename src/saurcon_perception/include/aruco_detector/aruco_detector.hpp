#ifndef ARUCO_DETECTOR_HPP
#define ARUCO_DETECTOR_HPP

#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>
#include <Eigen/Dense>
#include <vector>
#include <map>

namespace aruco_detector {

struct MarkerPose {
    int id;
    Eigen::Vector3d translation;
    Eigen::Matrix3d rotation;
    Eigen::Quaterniond quaternion;
    std::vector<cv::Point2f> corners;
    double confidence;
};

class ArucoDetector {
public:
    /**
     * @brief Constructor for ArUco detector
     * @param dictionary_id OpenCV ArUco dictionary ID (default: DICT_4X4_50)
     * @param marker_size Physical marker size in meters (default: 0.1524m)
     */
    ArucoDetector(int dictionary_id = cv::aruco::DICT_4X4_50, 
                  double marker_size = 0.1524);

    /**
     * @brief Detect ArUco markers in an image
     * @param image Input image (grayscale or color)
     * @param camera_matrix Camera intrinsic matrix (3x3)
     * @param dist_coeffs Camera distortion coefficients
     * @return Vector of detected marker poses
     */
    std::vector<MarkerPose> detectMarkers(
        const cv::Mat& image,
        const cv::Mat& camera_matrix,
        const cv::Mat& dist_coeffs);

    /**
     * @brief Draw detected markers on image for visualization
     * @param image Input/output image
     * @param markers Detected markers to draw
     */
    void drawMarkers(cv::Mat& image, const std::vector<MarkerPose>& markers);

    /**
     * @brief Set the marker size
     * @param size Marker size in meters
     */
    void setMarkerSize(double size);

    /**
     * @brief Get the marker size
     * @return Marker size in meters
     */
    double getMarkerSize() const;

    /**
     * @brief Convert rotation vector to Eigen rotation matrix
     * @param rvec OpenCV rotation vector
     * @return Eigen 3x3 rotation matrix
     */
    static Eigen::Matrix3d rvecToRotationMatrix(const cv::Vec3d& rvec);

    /**
     * @brief Convert rotation matrix to quaternion
     * @param rotation_matrix 3x3 rotation matrix
     * @return Eigen quaternion
     */
    static Eigen::Quaterniond rotationMatrixToQuaternion(const Eigen::Matrix3d& rotation_matrix);

private:
    cv::Ptr<cv::aruco::Dictionary> dictionary_;
    cv::Ptr<cv::aruco::DetectorParameters> detector_params_;
    double marker_size_;
};

} // namespace aruco_detector

#endif // ARUCO_DETECTOR_HPP
