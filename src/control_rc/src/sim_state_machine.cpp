#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <std_msgs/msg/u_int8.hpp>
#include "../include/types/saurcon_types.hpp"

#include <iostream>
#include <string>

class SaurconRcSim {
public:
	SaurconRcSim() : current_state(SaurconRCState::STANDBY) {}

	void run() {
		std::string input;
		print_state();
		while (true) {
			std::cout << "Enter state (standby/control/autonomous/exit): ";
			std::getline(std::cin, input);
			if (input == "exit") break;
			if (input == "standby") {
				handle_state_message(SaurconRCState::STANDBY);
			} else if (input == "control") {
				handle_state_message(SaurconRCState::RUN_CONTROL);
			} else if (input == "autonomous") {
				handle_state_message(SaurconRCState::RUN_AUTONOMOUS);
			} else {
				std::cout << "Unknown command. Try again.\n";
			}

			// Simulate velocity publishing in RUN_CONTROL or RUN_AUTONOMOUS
			if (current_state == SaurconRCState::RUN_CONTROL || current_state == SaurconRCState::RUN_AUTONOMOUS) {
				std::string vel_input;
				std::cout << "Enter velocity to publish (or blank to skip): ";
				std::getline(std::cin, vel_input);
				if (!vel_input.empty()) {
					try {
						double velocity = std::stod(vel_input);
						publish_velocity(velocity);
					} catch (...) {
						std::cout << "Invalid velocity input.\n";
					}
				}
			}
		}
	}

	SaurconRCState current_state;

	void handle_state_message(SaurconRCState new_state) {
		if (new_state == SaurconRCState::RUN_CONTROL && current_state != SaurconRCState::RUN_CONTROL) {
			std::cout << "Transition: " << state_name(current_state) << " -> RUN_CONTROL\n";
			current_state = SaurconRCState::RUN_CONTROL;
		} else if (new_state == SaurconRCState::RUN_AUTONOMOUS && current_state != SaurconRCState::RUN_AUTONOMOUS) {
			std::cout << "Transition: " << state_name(current_state) << " -> RUN_AUTONOMOUS\n";
			current_state = SaurconRCState::RUN_AUTONOMOUS;
		} else if (new_state == SaurconRCState::STANDBY && current_state != SaurconRCState::STANDBY) {
			std::cout << "Transition: " << state_name(current_state) << " -> STANDBY\n";
			current_state = SaurconRCState::STANDBY;
		} else {
			std::cout << "Already in " << state_name(current_state) << " state.\n";
		}
		print_state();
	}

private:


	void print_state() {
		std::cout << "Current state: " << state_name(current_state) << "\n";
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

	void publish_velocity(double velocity) {
		std::cout << "Publishing velocity: " << velocity << "\n";
		// Simulate actual publishing here if needed
	}
};

class SimCtrlBridge : public rclcpp::Node {
public:
	SimCtrlBridge(SaurconRcSim* sim) : Node("sim_ctrl_bridge"), sim_(sim) {
		// Subscribe to /ctrl_output
		sub_ctrl_output_ = this->create_subscription<geometry_msgs::msg::Twist>(
			"/ctrl_output", 10,
			std::bind(&SimCtrlBridge::ctrl_output_cb, this, std::placeholders::_1)
		);

		sub_state_cmd_output_ = this->create_subscription<std_msgs::msg::UInt8>(
			"/rc_state_cmd", 10,
			std::bind(&SimCtrlBridge::state_output_cb, this, std::placeholders::_1)
		);

		// Publisher to Gazebo bridge topic (update topic name as needed)
		pub_gz_cmd_ = this->create_publisher<geometry_msgs::msg::Twist>(
			"/model/rc_ackermann_vehicle/cmd_vel", 10
		);
		RCLCPP_INFO(this->get_logger(), "SimCtrlBridge node started.");
	}

private:
	rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr sub_ctrl_output_;
	rclcpp::Subscription<std_msgs::msg::UInt8>::SharedPtr sub_state_cmd_output_;
	rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_gz_cmd_;

	void ctrl_output_cb(const geometry_msgs::msg::Twist::SharedPtr msg) {
		// Republish to Gazebo bridge topic
		RCLCPP_INFO(this->get_logger(), "Republishing Twist: linear.x=%.3f angular.z=%.3f",
			msg->linear.x, msg->angular.z);
		pub_gz_cmd_->publish(*msg);
	}

	SaurconRcSim* sim_;
	void state_output_cb(const std_msgs::msg::UInt8::SharedPtr msg) {
		// Print out the state change command for now. eventually use it to change the state machine state
		RCLCPP_INFO(this->get_logger(), "State Change Commanded: %u", msg->data);
		SaurconRCState new_state = static_cast<SaurconRCState>(msg->data);
		if(sim_){
			sim_->handle_state_message(new_state);
		}
	}
};




int main() {
	// Start simulation state machine (existing logic)
	SaurconRcSim sim;
	std::thread sim_thread([&sim]() { sim.run(); });

	// Start ROS2 node for bridging control commands
	rclcpp::init(0, nullptr);
	auto bridge_node = std::make_shared<SimCtrlBridge>(&sim);
	rclcpp::spin(bridge_node);
	rclcpp::shutdown();

	sim_thread.join();
	return 0;
}
