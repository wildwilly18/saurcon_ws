#pragma once

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "std_msgs/msg/u_int8.hpp"
#include "geometry_msgs/msg/twist.hpp"

#include "types/saurcon_types.hpp"

#include "saurcon_rc/topic_bridge.hpp"

class StateMachine : public rclcpp::Node
{
public:
    StateMachine();
    void setState(SaurconState state);
    SaurconState getState() const;

private:
    void handleCurrentState();
    void onEnter(SaurconState state);
    void onExit(SaurconState state);
    
    //State Handlers
    void onEnter_STARTUP();
    void handle_STARTUP();

    void handle_STANDBY();

    //void onEnter_RUN_CONTROL();
    void handle_RUN_CONTROL();

    void handle_RUN_AUTONOMOUS();
    void auto_cmd_cb(const geometry_msgs::msg::Twist::SharedPtr msg);

    void onEnter_FAULT();
    void handle_FAULT();

    //Subscriber Callback
    void control_input_cb(const sensor_msgs::msg::Joy::SharedPtr msg);
    void saurcon_state_cb(const std_msgs::msg::UInt8::SharedPtr msg);

    //Publisher member functions
    std_msgs::msg::UInt8 rc_state_cmd_handler();

    void check_heartbeat();


    //Member Variables
    SaurconState current_state_;
    SaurconState previous_state_;

    rclcpp::TimerBase::SharedPtr state_timer_;
    rclcpp::TimerBase::SharedPtr state_pub_timer_;
    rclcpp::TimerBase::SharedPtr ctrl_pub_timer_;

    rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr  sub_joy;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr sub_auto_cmd;
    geometry_msgs::msg::Twist auto_msg;
    rclcpp::Time last_auto_cmd_;
    // Autonomous commands older than this are treated as lost and the car stops.
    const rclcpp::Duration auto_timeout_ = rclcpp::Duration::from_seconds(0.25);
    rclcpp::Subscription<std_msgs::msg::UInt8>::SharedPtr   sub_src_state;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_ctrl_cmd; 
    rclcpp::Publisher<std_msgs::msg::UInt8>::SharedPtr      pub_state_cmd;

    // Joystick mapping (parameters: throttle_axis, steer_axis, view_button, menu_button).
    // Defaults match a wired Xbox controller through joy_node.
    size_t throttle_idx = 1;
    size_t steer_idx    = 3;
    size_t view_idx     = 6;
    size_t menu_idx     = 7;

    geometry_msgs::msg::Twist ctrl_msg;
    geometry_msgs::msg::Twist joy_msg;
    geometry_msgs::msg::Twist stop_msg;

    std_msgs::msg::UInt8 desired_rc_state_msg;

    //Bridge
    std::unique_ptr<IMUBridge> imu_bridge_;

    //RC State
    SaurconRCState saurcon_rc_desired_state_{SaurconRCState::STANDBY};
    SaurconRCState saurcon_rc_current_state_{SaurconRCState::NO_STATE};

    float throttle{0.0f};
    float steer{0.0f};

    bool control_ready = false;

    rclcpp::Time menu_pressed_start_time;
    rclcpp::Time view_pressed_start_time;

    bool menu_held{false};
    bool menu_transition_triggered{false};
    bool view_held{false};
    bool view_transition_triggered{false};

    // Messaging handlers
    // /saurcon/state is published at 1 Hz, so allow a few missed messages.
    rclcpp::Time last_rc_heartbeat_;
    const rclcpp::Duration rc_timeout_ = rclcpp::Duration::from_seconds(3.0);

    rclcpp::Time last_ctrl_heartbeat_;
    const rclcpp::Duration ctrl_timeout_ = rclcpp::Duration::from_seconds(1.0);
    bool saurcon_rc_ready = 0;


};