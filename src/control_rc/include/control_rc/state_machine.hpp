#pragma once

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "std_msgs/msg/u_int8.hpp"
#include "geometry_msgs/msg/twist.hpp"

#include "types/saurcon_types.hpp"

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
    //void handle_STARTUP();

    void handle_STANDBY();

    //void onEnter_RUN_CONTROL();
    void handle_RUN_CONTROL();

    //void onEnter_RUN_AUTONOMOUS();
    //void handle_RUN_AUTONOMOUS();

    //void handle_FAULT();

    //Subscriber Callback
    void control_input_cb(const sensor_msgs::msg::Joy::SharedPtr msg);
    void saurcon_state_cb(const std_msgs::msg::UInt8::SharedPtr msg);

    // Variables
    SaurconState current_state_;
    SaurconState previous_state_;

    rclcpp::TimerBase::SharedPtr state_timer_;
    rclcpp::TimerBase::SharedPtr ctrl_pub_timer_;

    rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr  sub_joy;
    rclcpp::Subscription<std_msgs::msg::UInt8>::SharedPtr   sub_src_state;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_ctrl_cmd; 

    const size_t throttle_idx = 1;
    const size_t steer_idx    = 3;
    const size_t view_idx     = 6;
    const size_t menu_idx     = 7;

    geometry_msgs::msg::Twist ctrl_msg;
    geometry_msgs::msg::Twist joy_msg;
    geometry_msgs::msg::Twist stop_msg;

    float throttle;
    float steer;

    rclcpp::Time menu_pressed_start_time;
    rclcpp::Time view_pressed_start_time;

    bool menu_held;
    bool menu_transition_triggered;
    bool view_held;
    bool view_transition_triggered;


    bool saurcon_rc_ready = 0;


};