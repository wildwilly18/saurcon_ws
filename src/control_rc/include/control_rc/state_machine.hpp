#pragma once

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "std_msgs/msg/u_int8.hpp"
#include "geometry_msgs/msg/twist.hpp"

#include "types/saurcon_types.hpp"

#include "control_rc/topic_bridge.hpp"

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

    //void onEnter_RUN_AUTONOMOUS();
    //void handle_RUN_AUTONOMOUS();

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
    rclcpp::Subscription<std_msgs::msg::UInt8>::SharedPtr   sub_src_state;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_ctrl_cmd; 
    rclcpp::Publisher<std_msgs::msg::UInt8>::SharedPtr      pub_state_cmd;

    const size_t throttle_idx = 1;
    const size_t steer_idx    = 3;
    const size_t view_idx     = 6;
    const size_t menu_idx     = 7;

    geometry_msgs::msg::Twist ctrl_msg;
    geometry_msgs::msg::Twist joy_msg;
    geometry_msgs::msg::Twist stop_msg;

    std_msgs::msg::UInt8 desired_rc_state_msg;

    //Bridge
    std::unique_ptr<IMUBridge> imu_bridge_;

    //RC State
    SaurconRCState saurcon_rc_desired_state_;
    SaurconRCState saurcon_rc_current_state_;


    float throttle;
    float steer;

    bool control_ready = false;

    rclcpp::Time menu_pressed_start_time;
    rclcpp::Time view_pressed_start_time;

    bool menu_held;
    bool menu_transition_triggered;
    bool view_held;
    bool view_transition_triggered;

    // Messaging handlers
    rclcpp::Time last_rc_heartbeat_;
    const rclcpp::Duration rc_timeout_ = rclcpp::Duration::from_seconds(1.0);

    rclcpp::Time last_ctrl_heartbeat_;
    const rclcpp::Duration ctrl_timeout_ = rclcpp::Duration::from_seconds(1.0);
    bool saurcon_rc_ready = 0;


};