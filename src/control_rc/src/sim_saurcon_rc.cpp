
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <std_msgs/msg/u_int8.hpp>
#include "../include/types/saurcon_types.hpp"

class SaurconRcSim : public rclcpp::Node {
public:
	SaurconRcSim()
		: Node("saurcon_rc_sim"), current_state_(SaurconRCState::STANDBY)
	{
		sub_ctrl_output_ = this->create_subscription<geometry_msgs::msg::Twist>(
			"/ctrl_output", 10,
			std::bind(&SaurconRcSim::ctrl_output_cb, this, std::placeholders::_1)
		);

		sub_state_cmd_output_ = this->create_subscription<std_msgs::msg::UInt8>(
			"/rc_state_cmd", 10,
			std::bind(&SaurconRcSim::state_cmd_cb, this, std::placeholders::_1)
		);

		pub_gz_cmd_ = this->create_publisher<geometry_msgs::msg::Twist>(
			"/model/rc_ackermann_vehicle/cmd_vel", 10
		);

		pub_sim_state_output_ = this->create_publisher<std_msgs::msg::UInt8>(
			"/saurcon/state", 10
		);

		// Timer to publish state every second
		state_pub_timer_ = this->create_wall_timer(
			std::chrono::seconds(1),
			std::bind(&SaurconRcSim::publish_sim_state, this)
		);

		RCLCPP_INFO(this->get_logger(), "SaurconRcSim node started.");
	}

private:
	rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr sub_ctrl_output_;
	rclcpp::Subscription<std_msgs::msg::UInt8>::SharedPtr sub_state_cmd_output_;
	rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_gz_cmd_;
	rclcpp::Publisher<std_msgs::msg::UInt8>::SharedPtr pub_sim_state_output_;
	rclcpp::TimerBase::SharedPtr state_pub_timer_;

	SaurconRCState current_state_;

	void ctrl_output_cb(const geometry_msgs::msg::Twist::SharedPtr msg) {
		// Only publish velocity if in correct state
		if (current_state_ == SaurconRCState::RUN_CONTROL || current_state_ == SaurconRCState::RUN_AUTONOMOUS) {
			RCLCPP_INFO(this->get_logger(), "Publishing to Gazebo: linear.x=%.3f angular.z=%.3f", msg->linear.x, msg->angular.z);
			pub_gz_cmd_->publish(*msg);
		}
	}

	void state_cmd_cb(const std_msgs::msg::UInt8::SharedPtr msg) {
		SaurconRCState new_state = static_cast<SaurconRCState>(msg->data);
		if (new_state != current_state_) {
			RCLCPP_INFO(this->get_logger(), "State change: %s -> %s", state_name(current_state_).c_str(), state_name(new_state).c_str());
			current_state_ = new_state;
			publish_sim_state();
		} else {
			RCLCPP_INFO(this->get_logger(), "Already in state: %s", state_name(current_state_).c_str());
		}
	}

	void publish_sim_state() {
		std_msgs::msg::UInt8 msg;
		msg.data = static_cast<uint8_t>(current_state_);
		pub_sim_state_output_->publish(msg);
		RCLCPP_INFO(this->get_logger(), "Published sim state: %s", state_name(current_state_).c_str());
	}

	std::string state_name(SaurconRCState state) {
		switch (state) {
			case SaurconRCState::NO_STATE: return "NO_STATE";
			case SaurconRCState::STARTUP: return "STARTUP";
			case SaurconRCState::STARTUP_ROS: return "STARTUP_ROS";
			case SaurconRCState::SETUP: return "SETUP";
			case SaurconRCState::STANDBY: return "STANDBY";
			case SaurconRCState::RUN_CONTROL: return "RUN_CONTROL";
			case SaurconRCState::RUN_AUTONOMOUS: return "RUN_AUTONOMOUS";
			case SaurconRCState::FAULT: return "FAULT";
			case SaurconRCState::FAULT_ROS: return "FAULT_ROS";
			default: return "UNKNOWN";
		}
	}
};

int main(int argc, char* argv[]) {
	rclcpp::init(argc, argv);
	auto node = std::make_shared<SaurconRcSim>();
	rclcpp::spin(node);
	rclcpp::shutdown();
	return 0;
}
