#include "aruco_detector.hpp"
#include "Eigen/Dense"

#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <map>
#include <algorithm>
#include <cmath>

namespace fs = std::filesystem;

int main(int argc, char** argv){
    std::cout << "====== ARUCO Class Test ======" << std::endl;

    std::string camera_json = "config/camera_params.json";
    std::string marker_json = "config/marker_params.json";
    auto detector = aruco_detector(camera_json, marker_json);

    const fs::path debug_dir = "/home/wilson-desktop/saurcon_ws/src/saurcon_perception/data/output/class_test_debug";
    fs::create_directories(debug_dir);

    cv::Ptr<cv::aruco::DetectorParameters> detectorParams = cv::aruco::DetectorParameters::create();
    detectorParams->adaptiveThreshWinSizeMin  = 3;
    detectorParams->adaptiveThreshWinSizeMax  = 101;
    detectorParams->adaptiveThreshWinSizeStep = 4;
    detectorParams->adaptiveThreshConstant    = 7.0;
    detectorParams->errorCorrectionRate       = 0.6;
    detectorParams->minMarkerPerimeterRate    = 0.01;
    detectorParams->maxMarkerPerimeterRate    = 4.0;
    detectorParams->cornerRefinementMethod    = cv::aruco::CORNER_REFINE_SUBPIX;
    detectorParams->detectInvertedMarker      = true;
    cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);

    std::vector<std::string> image_paths;
    if (argc > 1) {
        for (int i = 1; i < argc; ++i) {
            image_paths.emplace_back(argv[i]);
        }
    } else {
        image_paths = {
            "/home/wilson-desktop/saurcon_ws/src/saurcon_perception/data/test_images/frame_000006_1780227470.301049.png",
            "/home/wilson-desktop/saurcon_ws/src/saurcon_perception/data/test_images/frame_000029_1780227471.813807.png",
            "/home/wilson-desktop/saurcon_ws/src/saurcon_perception/data/test_images/frame_000045_1780227472.873918.png"
        };
    }

    for (const auto& image_path : image_paths) {
        cv::Mat img = cv::imread(image_path);

        std::cout << "\nImage: " << std::filesystem::path(image_path).filename().string() << std::endl;

        if (img.empty()) {
            std::cout << "  [ERROR] Could not load image: " << image_path << std::endl;
            continue;
        }

        cv::Mat detector_img = img.clone();
        auto tags = detector.getTagsInImage(detector_img);

        cv::Mat gray;
        if (img.channels() > 1) {
            cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY);
        } else {
            gray = img.clone();
        }

        cv::Mat clahe_img;
        cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(2.5, cv::Size(8, 8));
        clahe->apply(gray, clahe_img);

        struct PassResult {
            std::string name;
            std::vector<int> ids;
            std::vector<std::vector<cv::Point2f>> corners;
            std::vector<std::vector<cv::Point2f>> rejected;
            cv::Mat image;
        };

        std::vector<PassResult> passes;
        auto run_pass = [&](const std::string& name, const cv::Mat& pass_img) {
            PassResult pass;
            pass.name = name;
            pass.image = pass_img;
            cv::aruco::detectMarkers(pass.image, dictionary, pass.corners, pass.ids, detectorParams, pass.rejected);
            passes.push_back(pass);
        };

        // CLAHE-only test pass for quick isolated validation.
        run_pass("clahe", clahe_img);

        std::map<int, int> id_votes;
        for (const auto& pass : passes) {
            for (int id : pass.ids) {
                id_votes[id]++;
            }
        }

        std::vector<int> stable_ids;
        for (const auto& kv : id_votes) {
            if (kv.second >= 2) {
                stable_ids.push_back(kv.first);
            }
        }

        auto best_it = std::max_element(
            passes.begin(),
            passes.end(),
            [](const PassResult& a, const PassResult& b) { return a.ids.size() < b.ids.size(); });

        if (stable_ids.empty() && best_it != passes.end()) {
            stable_ids = best_it->ids;
        }

        // Pose recovery for camera location relative to detected marker(s)
        // using a pinhole model from image width and configured horizontal FOV.
        const double horizontal_fov = 1.204;  // rad, from camera_params.json
        const double fx = static_cast<double>(img.cols) / (2.0 * std::tan(horizontal_fov / 2.0));
        const double fy = fx;
        const double cx = static_cast<double>(img.cols) / 2.0;
        const double cy = static_cast<double>(img.rows) / 2.0;

        cv::Mat camMatrix = (cv::Mat_<double>(3, 3) <<
            fx, 0.0, cx,
            0.0, fy, cy,
            0.0, 0.0, 1.0);
        cv::Mat distCoeffs = cv::Mat::zeros(5, 1, CV_64F);

        const float marker_len = 0.1524f;  // Matches marker_params.json and sim marker size.
        cv::Mat objPoints(4, 1, CV_32FC3);
        objPoints.ptr<cv::Vec3f>(0)[0] = cv::Vec3f(-marker_len / 2.0f, marker_len / 2.0f, 0.0f);
        objPoints.ptr<cv::Vec3f>(0)[1] = cv::Vec3f( marker_len / 2.0f, marker_len / 2.0f, 0.0f);
        objPoints.ptr<cv::Vec3f>(0)[2] = cv::Vec3f( marker_len / 2.0f,-marker_len / 2.0f, 0.0f);
        objPoints.ptr<cv::Vec3f>(0)[3] = cv::Vec3f(-marker_len / 2.0f,-marker_len / 2.0f, 0.0f);

        // Camera optical frame -> vehicle/base frame (same convention as aruco_detector).
        cv::Matx33d R_vc(
            0,  0,  1,
           -1,  0,  0,
            0, -1,  0
        );
        cv::Vec3d t_vc(0.219, 0.0, 0.05);  // from config/camera_params.json
        cv::Matx44d T_vc = makeT(R_vc, t_vc);
        int total_rejected = 0;
        for (const auto& pass : passes) {
            total_rejected += static_cast<int>(pass.rejected.size());
        }

        cv::Mat debugBgr;
        cv::cvtColor(best_it->image, debugBgr, cv::COLOR_GRAY2BGR);
        if (!best_it->ids.empty()) {
            cv::aruco::drawDetectedMarkers(debugBgr, best_it->corners, best_it->ids);
        }
        if (!best_it->rejected.empty()) {
            cv::aruco::drawDetectedMarkers(debugBgr, best_it->rejected, cv::noArray(), cv::Scalar(0, 0, 255));
        }

        const std::string base_name = fs::path(image_path).stem().string();
        const fs::path clahe_path = debug_dir / (base_name + "_clahe.png");
        const fs::path dbg_path = debug_dir / (base_name + "_debug.png");

        cv::imwrite(clahe_path.string(), clahe_img);
        cv::imwrite(dbg_path.string(), debugBgr);

        std::cout << "  Debug: " << dbg_path.string() << std::endl;
        std::cout << "  CLAHE: " << clahe_path.string() << std::endl;
        std::cout << "  Best pass: " << best_it->name << " | detections=" << best_it->ids.size() << std::endl;
        std::cout << "  Rejected candidates (all passes): " << total_rejected << std::endl;

        std::cout << "  ID votes:";
        if (id_votes.empty()) {
            std::cout << " none";
        } else {
            for (const auto& kv : id_votes) {
                std::cout << " " << kv.first << "(" << kv.second << ")";
            }
        }
        std::cout << std::endl;

        std::cout << "  Stable IDs:";
        if (stable_ids.empty()) {
            std::cout << " none";
        } else {
            for (int id : stable_ids) {
                std::cout << " " << id;
            }
        }
        std::cout << std::endl;

        const bool has0 = std::find(stable_ids.begin(), stable_ids.end(), 0) != stable_ids.end();
        const bool has1 = std::find(stable_ids.begin(), stable_ids.end(), 1) != stable_ids.end();
        std::cout << "  Consistency check -> tag0=" << (has0 ? "YES" : "NO")
                  << " tag1=" << (has1 ? "YES" : "NO") << std::endl;

        if (!best_it->ids.empty()) {
            std::cout << "  Camera location in marker frame (per detection):" << std::endl;
            for (size_t i = 0; i < best_it->ids.size(); ++i) {
                cv::Vec3d rvec;
                cv::Vec3d tvec;
                bool ok = cv::solvePnP(objPoints, best_it->corners[i], camMatrix, distCoeffs, rvec, tvec);
                if (!ok) {
                    std::cout << "    tag " << best_it->ids[i] << ": solvePnP failed" << std::endl;
                    continue;
                }

                cv::Matx33d R_cm = rodriguesToMatx33d(rvec);
                cv::Matx44d T_cm = makeT(R_cm, tvec);
                cv::Matx44d T_mc = T_cm.inv();

                const double cam_x = T_mc(0, 3);
                const double cam_y = T_mc(1, 3);
                const double cam_z = T_mc(2, 3);
                cv::Matx44d T_vm = T_vc * T_cm;
                cv::Matx44d T_mv = T_vm.inv();
                const double base_x = T_mv(0, 3);
                const double base_y = T_mv(1, 3);
                const double base_z = T_mv(2, 3);
                const double range = std::sqrt(tvec[0] * tvec[0] + tvec[1] * tvec[1] + tvec[2] * tvec[2]);

                std::cout << "    tag " << best_it->ids[i]
                          << " | marker_in_cam tvec=[" << tvec[0] << ", " << tvec[1] << ", " << tvec[2] << "]"
                          << " | cam_in_marker=[" << cam_x << ", " << cam_y << ", " << cam_z << "]"
                          << " | marker_in_base=[" << T_vm(0,3) << ", " << T_vm(1,3) << ", " << T_vm(2,3) << "]"
                          << " | base_in_marker=[" << base_x << ", " << base_y << ", " << base_z << "]"
                          << " | range=" << range << " m" << std::endl;
            }
        }

        if (tags.empty()) {
            std::cout << "  Pose solve (aruco_detector): no tags." << std::endl;
            continue;
        }

        for (const auto& tag : tags) {
            std::cout << "  [ Pose Marker ID : " << tag.tag_id << " ] tvec | "
                      << tag.tag_pose(0,3) << " "
                      << tag.tag_pose(1,3) << " "
                      << tag.tag_pose(2,3) << std::endl;
        }
    }
    
    return 0;
}
