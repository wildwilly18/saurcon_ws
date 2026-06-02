#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <saurcon_perception/msg/aruco_pose_array.hpp>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <boost/json.hpp>

#include <fstream>
#include <sstream>
#include <map>
#include <cmath>

// ---------------------------------------------------------------------------
// ArucoLocalizerNode
//
// Subscribes to ArucoPoseArray (detections in camera optical frame).
// For each detected marker whose ID is in the marker map CSV, computes
// the robot's world pose and publishes it as PoseWithCovarianceStamped.
//
// Frame chain:
//   T_cm  : marker in camera frame          (from detector)
//   T_vc  : camera frame → vehicle/base_link (from camera_params.json)
//   T_vm  : marker in vehicle frame         = T_vc * T_cm
//   T_wm  : marker in world frame           (from marker_map.csv)
//   T_wv  : vehicle in world frame          = T_wm * inv(T_vm)  ← what we publish
// ---------------------------------------------------------------------------

namespace json = boost::json;

class ArucoLocalizerNode : public rclcpp::Node
{
public:
	ArucoLocalizerNode() : Node("aruco_localizer")
	{
		std::string pkg_share = ament_index_cpp::get_package_share_directory("saurcon_perception");

		this->declare_parameter("aruco_topic",        "/aruco_poses");
		this->declare_parameter("localization_topic", "/saurcon/aruco_localization");
		this->declare_parameter("camera_params",      pkg_share + "/config/camera_params.json");
		this->declare_parameter("marker_map_csv",     pkg_share + "/config/marker_map.csv");
		// Measurement noise: how accurate is an ArUco-derived pose (1-sigma)
		this->declare_parameter("position_std",    0.1);  // metres
		this->declare_parameter("orientation_std", 0.1);  // radians

		pos_std_ = this->get_parameter("position_std").as_double();
		ori_std_ = this->get_parameter("orientation_std").as_double();

		loadCameraTransform(this->get_parameter("camera_params").as_string());
		loadMarkerMap(this->get_parameter("marker_map_csv").as_string());

		sub_ = this->create_subscription<saurcon_perception::msg::ArucoPoseArray>(
			this->get_parameter("aruco_topic").as_string(), 10,
			std::bind(&ArucoLocalizerNode::detectionCb, this, std::placeholders::_1));

		pub_ = this->create_publisher<geometry_msgs::msg::PoseWithCovarianceStamped>(
			this->get_parameter("localization_topic").as_string(), 10);

		RCLCPP_INFO(this->get_logger(),
			"ArucoLocalizer started. %zu markers loaded. "
			"pos_std=%.3fm  ori_std=%.3frad",
			marker_map_.size(), pos_std_, ori_std_);
	}

private:
	// T_vc_: transforms a point in camera optical frame to vehicle (base_link) frame.
	// Matches the convention in aruco_detector.cpp:
	//   Camera: X=right, Y=down, Z=forward
	//   Vehicle: X=forward, Y=left, Z=up
	Eigen::Matrix4d T_vc_ = Eigen::Matrix4d::Identity();

	// marker_id → T_wm (4x4 homogeneous world pose of the marker)
	std::map<int, Eigen::Matrix4d> marker_map_;

	double pos_std_;
	double ori_std_;

	rclcpp::Subscription<saurcon_perception::msg::ArucoPoseArray>::SharedPtr sub_;
	rclcpp::Publisher<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr pub_;

	// ------------------------------------------------------------------
	// Load camera→vehicle transform from camera_params.json.
	// Uses the same rotation convention as aruco_detector.cpp.
	// ------------------------------------------------------------------
	void loadCameraTransform(const std::string& path)
	{
		std::ifstream file(path);
		if (!file.is_open()) throw std::runtime_error("Cannot open camera params: " + path);
		std::stringstream buf; buf << file.rdbuf();
		auto j = json::parse(buf.str());

		double tx = j.at("transform").at("translation").at("x").as_double();
		double ty = j.at("transform").at("translation").at("y").as_double();
		double tz = j.at("transform").at("translation").at("z").as_double();

		// Camera X=right, Y=down, Z=forward  →  Vehicle X=forward, Y=left, Z=up
		Eigen::Matrix3d R_vc;
		R_vc <<  0,  0,  1,
		        -1,  0,  0,
		         0, -1,  0;

		T_vc_.setIdentity();
		T_vc_.block<3,3>(0,0) = R_vc;
		T_vc_.block<3,1>(0,3) = Eigen::Vector3d(tx, ty, tz);

		RCLCPP_INFO(this->get_logger(),
			"Camera→vehicle transform: t=[%.3f, %.3f, %.3f]", tx, ty, tz);
	}

	// ------------------------------------------------------------------
	// Load marker world poses from CSV.
	// Format (one row per marker):
	//   id,x,y,z,phi,theta,psi   (ZYX Euler angles, SDF/world convention)
	//
	// phi/theta/psi match the SDF <pose> roll/pitch/yaw, so all vertically
	// mounted markers have phi=theta=0 and only psi (yaw) varies.
	//
	// A fixed ArUco frame correction Q_ARUCO_FRAME is post-multiplied to
	// convert from the SDF model frame (face normal = local X) to the ArUco
	// detection frame (face normal = local Z, as per solvePnP objPoints).
	// Lines beginning with '#' are treated as comments and skipped.
	// ------------------------------------------------------------------
	void loadMarkerMap(const std::string& path)
	{
		std::ifstream file(path);
		if (!file.is_open()) {
			RCLCPP_WARN(this->get_logger(),
				"Marker map CSV not found: %s  — localizer will produce no output.", path.c_str());
			return;
		}

		// Fixed rotation: ArUco frame (Z=outward) → SDF model frame (X=outward).
		// R = [[0,0,1],[1,0,0],[0,1,0]]  ≈  120° about [1,1,1]/√3
		// As quaternion: (w=0.5, x=0.5, y=0.5, z=0.5)
		const Eigen::Quaterniond Q_ARUCO_FRAME(0.5, 0.5, 0.5, 0.5);

		std::string line;

		while (std::getline(file, line)) {
			if (line.empty() || line[0] == '#') continue;

			std::istringstream ss(line);
			std::string tok;
			std::vector<std::string> tokens;
			while (std::getline(ss, tok, ',')) tokens.push_back(tok);

			// Skip the header row (first non-comment line starting with 'id')
			if (tokens[0] == "id") continue;

			if (tokens.size() < 7) {
				RCLCPP_WARN(this->get_logger(), "Skipping malformed CSV line: %s", line.c_str());
				continue;
			}

			int    id    = std::stoi(tokens[0]);
			double x     = std::stod(tokens[1]);
			double y     = std::stod(tokens[2]);
			double z     = std::stod(tokens[3]);
			double phi   = std::stod(tokens[4]);  // roll  (SDF convention)
			double theta = std::stod(tokens[5]);  // pitch (SDF convention)
			double psi   = std::stod(tokens[6]);  // yaw   (SDF convention)

			// SDF frame: q_sdf = Rz(psi) * Ry(theta) * Rx(phi)
			Eigen::Quaterniond q_sdf =
				Eigen::AngleAxisd(psi,   Eigen::Vector3d::UnitZ()) *
				Eigen::AngleAxisd(theta, Eigen::Vector3d::UnitY()) *
				Eigen::AngleAxisd(phi,   Eigen::Vector3d::UnitX());

			// Convert to ArUco detection frame (solvePnP: marker face in XY plane,
			// Z = outward toward camera). SDF model frame has face normal = local X.
			Eigen::Quaterniond q = (q_sdf * Q_ARUCO_FRAME).normalized();

			Eigen::Matrix4d T = Eigen::Matrix4d::Identity();
			T.block<3,3>(0,0) = q.toRotationMatrix();
			T(0,3) = x;  T(1,3) = y;  T(2,3) = z;

			marker_map_[id] = T;
			RCLCPP_DEBUG(this->get_logger(),
				"Marker %d loaded at world (%.3f, %.3f, %.3f)", id, x, y, z);
		}
		RCLCPP_INFO(this->get_logger(), "Loaded %zu marker world poses from CSV.", marker_map_.size());
	}

	// ------------------------------------------------------------------
	// Build 4x4 homogeneous matrix from a geometry_msgs::Pose.
	// ------------------------------------------------------------------
	static Eigen::Matrix4d poseToMatrix(const geometry_msgs::msg::Pose& p)
	{
		// Eigen Quaterniond constructor: (w, x, y, z)
		Eigen::Quaterniond q(
			p.orientation.w, p.orientation.x,
			p.orientation.y, p.orientation.z);
		q.normalize();

		Eigen::Matrix4d T = Eigen::Matrix4d::Identity();
		T.block<3,3>(0,0) = q.toRotationMatrix();
		T(0,3) = p.position.x;
		T(1,3) = p.position.y;
		T(2,3) = p.position.z;
		return T;
	}

	// ------------------------------------------------------------------
	// Callback: for each detection, compute vehicle world pose and publish.
	// Multiple detections in one frame generate one message each — the UKF
	// handles fusing multiple measurements.
	// ------------------------------------------------------------------
	void detectionCb(const saurcon_perception::msg::ArucoPoseArray::SharedPtr msg)
	{
		for (const auto& detection : msg->poses) {
			auto it = marker_map_.find(detection.tag_id);
			if (it == marker_map_.end()) {
				RCLCPP_DEBUG(this->get_logger(),
					"Marker ID %d not in map — skipping.", detection.tag_id);
				continue;
			}

			// T_cm: marker pose in camera optical frame (from detector)
			Eigen::Matrix4d T_cm = poseToMatrix(detection.pose.pose);

			// T_vm: marker pose in vehicle (base_link) frame
			Eigen::Matrix4d T_vm = T_vc_ * T_cm;

			// T_wm: known world pose of this marker
			const Eigen::Matrix4d& T_wm = it->second;

			// T_wv: vehicle pose in world frame
			// Derivation: T_wv * T_vm = T_wm  →  T_wv = T_wm * T_vm⁻¹
			Eigen::Matrix4d T_wv = T_wm * T_vm.inverse();

			// Extract position and yaw (robot is nominally flat, so only Z-rotation matters)
			double x   = T_wv(0,3);
			double y   = T_wv(1,3);
			double z   = T_wv(2,3);
			double yaw = std::atan2(T_wv(1,0), T_wv(0,0));

			Eigen::Quaterniond q_out(Eigen::AngleAxisd(yaw, Eigen::Vector3d::UnitZ()));

			// Build output message
			geometry_msgs::msg::PoseWithCovarianceStamped out;
			out.header.stamp    = msg->header.stamp;
			out.header.frame_id = "map";

			out.pose.pose.position.x    = x;
			out.pose.pose.position.y    = y;
			out.pose.pose.position.z    = z;
			out.pose.pose.orientation.x = q_out.x();
			out.pose.pose.orientation.y = q_out.y();
			out.pose.pose.orientation.z = q_out.z();
			out.pose.pose.orientation.w = q_out.w();

			// Diagonal covariance [x, y, z, roll, pitch, yaw] (6x6, row-major)
			double pvar = pos_std_ * pos_std_;
			double ovar = ori_std_ * ori_std_;
			out.pose.covariance[0]  = pvar;  // x
			out.pose.covariance[7]  = pvar;  // y
			out.pose.covariance[14] = pvar;  // z  (less trusted for a ground robot)
			out.pose.covariance[21] = ovar;  // roll
			out.pose.covariance[28] = ovar;  // pitch
			out.pose.covariance[35] = ovar;  // yaw

			pub_->publish(out);

			RCLCPP_DEBUG(this->get_logger(),
				"Marker %d → robot (x=%.3f, y=%.3f, yaw=%.3f°)",
				detection.tag_id, x, y, yaw * 180.0 / M_PI);
		}
	}
};

int main(int argc, char** argv)
{
	rclcpp::init(argc, argv);
	auto node = std::make_shared<ArucoLocalizerNode>();
	rclcpp::spin(node);
	rclcpp::shutdown();
	return 0;
}
