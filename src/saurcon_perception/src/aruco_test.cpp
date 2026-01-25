#include "aruco_detector.hpp"
#include "Eigen/Dense"

#include <iostream>

int main(){
    std::cout << "====== ARUCO PLAYGROUND ======" << std::endl;

    // Camera intrinsics from camera_params.json
    cv::Mat camMatrix = (cv::Mat_<double>(3,3) << 
        929.4, 0.0, 640.0,
        0.0, 929.4, 400.0,
        0.0, 0.0, 1.0);
    
    cv::Mat distCoeffs = cv::Mat::zeros(5, 1, CV_64F);  // No distortion coefficients provided zeros from sim.

    std::string image_path = "data/test_images/frame_000001_1766246134.933204.png";
    // Read in the image
    cv::Mat image = cv::imread(image_path, cv::IMREAD_COLOR);

    //Check if image is empty
    if(image.empty()){
        std::cout << "Image Non-Existent: Shutting down." << std::endl;
        return 0;
    }

    std::cout << "Image loaded successfully: " << image.cols << "x" << image.rows << std::endl;

    // Convert to grayscale for better detection
    cv::Mat grayImage;
    cv::cvtColor(image, grayImage, cv::COLOR_BGR2GRAY);

    cv::Mat eqImage;
    cv::threshold(grayImage, eqImage, 50, 255, cv::THRESH_BINARY);

    // Set up ArUco detection parameters
    std::vector<int> markerIds;
    std::vector<std::vector<cv::Point2f>> markerCorners, rejectedCandidates;
    cv::Ptr<cv::aruco::DetectorParameters> detectorParams = cv::aruco::DetectorParameters::create();

    // Set up the camera to vehicle transform
    cv::Matx33d R_vc = cv::Matx33d::eye();
    cv::Vec3d  t_vc(0.219, 0, 0.05);
    cv::Matx44d T_vc = makeT(R_vc, t_vc);
    
    // Use DICT_4X4_50 dictionary
    cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);
    
    // Detect markers using enhanced image (try both)
    cv::aruco::detectMarkers(eqImage, dictionary, markerCorners, markerIds, detectorParams, rejectedCandidates);
    
    std::cout << "Detected " << markerIds.size() << " markers (grayscale)" << std::endl;
    
    // If nothing found, try binary image
    if (markerIds.empty()) {
        cv::aruco::detectMarkers(grayImage, dictionary, markerCorners, markerIds, detectorParams, rejectedCandidates);
        std::cout << "Detected " << markerIds.size() << " markers (binary)" << std::endl;
    }
    if (!markerIds.empty()) {
        std::cout << "Marker IDs: ";
        for (size_t i = 0; i < markerIds.size(); i++) {
            std::cout << markerIds[i];
            if (i < markerIds.size() - 1) std::cout << ", ";
        }
        std::cout << std::endl;
    }
    
    // Draw detected markers on image
    cv::Mat outputImage = image.clone();
    if (!markerIds.empty()) {
        cv::aruco::drawDetectedMarkers(outputImage, markerCorners, markerIds);
    }
    
    // Save enhanced grayscale image
    std::string gray_output_path = "data/output/gray_test_output.png";
    cv::imwrite(gray_output_path, grayImage);
    std::cout << "Gray image saved to: " << gray_output_path << std::endl;

    // Save enhanced grayscale image
    std::string eq_output_path = "data/output/eq_test_output.png";
    cv::imwrite(eq_output_path, eqImage);
    std::cout << "EQ image saved to: " << eq_output_path << std::endl;

    // Save binary image
    std::string output_path = "data/output/test_output.png";
    cv::imwrite(output_path, outputImage);
    std::cout << "Output image saved to: " << output_path << std::endl;

    // Set coordinate system for the marker
    float box_size = 0.1524;
    float border_ratio = 1.0/6.0;
    float border_width = box_size * border_ratio;

    float markerLength = box_size - (2*border_width);

    std::cout << "Marker Length: " << markerLength << std::endl;

    cv::Mat objPoints(4,1, CV_32FC3);
    objPoints.ptr<cv::Vec3f>(0)[0] = cv::Vec3f(-markerLength/2.f, markerLength/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[1] = cv::Vec3f(markerLength/2.f, markerLength/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[2] = cv::Vec3f(markerLength/2.f, -markerLength/2.f, 0);
    objPoints.ptr<cv::Vec3f>(0)[3] = cv::Vec3f(-markerLength/2.f, -markerLength/2.f, 0);

    // Estimate pose from the id of zero.
    size_t nMarkers = markerCorners.size();
    std::vector<cv::Vec3d> rvecs(nMarkers), tvecs(nMarkers);

    if(!markerIds.empty()){
        std::cout << "Identifying Marker locations " << std::endl;
        
        for(size_t i = 0; i < nMarkers; ++i){
            cv::solvePnP(objPoints, markerCorners.at(i), camMatrix, distCoeffs, rvecs.at(i), tvecs.at(i));
            std::cout << "[ Marker ID: " << markerIds.at(i) << "] TVecs X: " << tvecs.at(i)[0] << " Y: " << tvecs.at(i)[1] << " Z: " << tvecs.at(i)[2] << std::endl;
            std::cout << "[ Marker ID: " << markerIds.at(i) << "] RVecs X: " << rvecs.at(i)[0] << " Y: " << rvecs.at(i)[1] << " Z: " << rvecs.at(i)[2] << std::endl;

            //Build the marker to camera transform
            cv::Vec3d rvec_cm = rvecs.at(i);
            cv::Vec3d tvec_cm = tvecs.at(i);

            cv::Matx33d R_cm = rodriguesToMatx33d(rvec_cm);
            cv::Matx44d T_cm = makeT(R_cm, tvec_cm);

            cv::Matx44d T_vm = T_vc * T_cm;

            //Extracted pose
            cv::Matx33d R_vm(
                T_vm(0,0), T_vm(0,1), T_vm(0,2),
                T_vm(1,0), T_vm(1,1), T_vm(1,2),
                T_vm(2,0), T_vm(2,1), T_vm(2,2)
            );

            cv::Vec3d t_vm(T_vm(0,3), T_vm(1,3), T_vm(2,3));

            cv::Vec3d rvec_vm;
            cv::Rodrigues(cv::Mat(R_vm), rvec_vm);

            std::cout << "marker position in vehicle frame: " << t_vm << "\n";
            std::cout << "marker rvec in vehicle frame: " << R_vm << "\n";

        }
    }

    return 0;
}
