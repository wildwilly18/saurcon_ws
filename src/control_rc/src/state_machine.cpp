#include "control_rc/state_machine.hpp"

using namespace std;

StateMachine::StateMachine()
: Node("saurcon_state_machine"),
  current_state_(SaurconState::STARTUP),
  previous_state_(SaurconState::STARTUP)
  {
    RCLCPP_INFO(get_logger(), "State Machine Initialized");

    state_timer_ = this->create_wall_timer(
        30ms, std::bind(&StateMachine::handleCurrentState, this)
    );

    stop_msg.linear.x  = 0.0;
    stop_msg.angular.z = 0.0;
    ctrl_msg.linear.x  = 0.0;
    ctrl_msg.angular.z = 0.0;

    pub_ctrl_cmd = this->create_publisher<geometry_msgs::msg::Twist>(
    "/ctrl_output", 10
    );

    //Create Wall Timer for publisher
    ctrl_pub_timer_ = this->create_wall_timer(30ms,
        [this] () {
            if (current_state_ == SaurconState::RUN_CONTROL || current_state_ == SaurconState::RUN_AUTONOMOUS){
                pub_ctrl_cmd->publish(ctrl_msg);
            } else {
                pub_ctrl_cmd->publish(stop_msg);
            }
        }
    );

    //Enter into Standby enter handler
    onEnter(current_state_);
}

void StateMachine::setState(SaurconState newState)
{
    if (newState == current_state_) return;

    onExit(current_state_);
    previous_state_ = current_state_;
    current_state_  = newState;
    onEnter(newState);
}

SaurconState StateMachine::getState() const { return current_state_;}

void StateMachine::handleCurrentState()
{
    switch (current_state_) {
        case SaurconState::STANDBY:        handle_STANDBY();        break;
        case SaurconState::STARTUP:        handle_STARTUP();        break;
        case SaurconState::RUN_CONTROL:    handle_RUN_CONTROL();    break;
        case SaurconState::RUN_AUTONOMOUS: break;
        case SaurconState::FAULT:          break;
        default: break;
    }
}

void StateMachine::onEnter(SaurconState state){
    RCLCPP_INFO(get_logger(), "Entering State [%d]: %s", static_cast<int>(state), 
        (state == SaurconState::STARTUP ? "STARTUP" :
         state == SaurconState::STANDBY ? "STANDBY" :
         state == SaurconState::RUN_CONTROL ? "RUN_CONTROL" :
         state == SaurconState::RUN_AUTONOMOUS ? "RUN_AUTONOMOUS" :
         state == SaurconState::FAULT ? "FAULT" : "UNKNOWN"));
    
    switch(state) {
        case SaurconState::STARTUP: onEnter_STARTUP(); break;
        default: break;
    }
}

void StateMachine::onExit(SaurconState state){
    RCLCPP_INFO(get_logger(), "Exiting State [%d]: %s", static_cast<int>(state), 
        (state == SaurconState::STARTUP ? "STARTUP" :
         state == SaurconState::STANDBY ? "STANDBY" :
         state == SaurconState::RUN_CONTROL ? "RUN_CONTROL" :
         state == SaurconState::RUN_AUTONOMOUS ? "RUN_AUTONOMOUS" :
         state == SaurconState::FAULT ? "FAULT" : "UNKNOWN"));
    //Not sure if any exit state handlers really needed.
}

void StateMachine::onEnter_STARTUP(){
    // While in setup initialize our subscribers and transition to standby
    sub_joy = this->create_subscription<sensor_msgs::msg::Joy>(
        "/joy", 10,
        bind(&StateMachine::control_input_cb, this, placeholders::_1)
    );

    sub_src_state = this->create_subscription<std_msgs::msg::UInt8>(
        "/saurcon/state", 10,
        bind(&StateMachine::saurcon_state_cb, this, placeholders::_1)
    );

    //TODO: add some logic here likely to watch for a heartbeat from uRos then send to standby
    StateMachine::setState(SaurconState::STANDBY);
}

void StateMachine::handle_STARTUP(){
    if(saurcon_rc_ready){
        StateMachine::setState(SaurconState::STANDBY);
    }
}

void StateMachine::handle_STANDBY(){
    //Initilization is done. Look for a menu press and hold or view press and hold to send us to autonomous or rc control
    if (menu_held){
        if(!menu_transition_triggered) {
            if((this->now() - this->menu_pressed_start_time).seconds() >= 2.0) {
                StateMachine::setState(SaurconState::RUN_CONTROL);
                menu_transition_triggered = true;
            }
        }
    }
}

void StateMachine::handle_RUN_CONTROL(){
    //Always verify we have heartbeat
    StateMachine::check_heartbeat();

    // Watch for button presses to send us back into Standby mode.
    if (menu_held) {
        if(!menu_transition_triggered) {
            if((this->now() - this->menu_pressed_start_time).seconds() >=2.0) {
                StateMachine::setState(SaurconState::STANDBY);
                menu_transition_triggered = true;
            }
        }
    }

    if (view_held) {
        if(!view_transition_triggered) {
            if((this->now() - this->view_pressed_start_time).seconds() >= 2.0) {
                StateMachine::setState(SaurconState::STANDBY);
                view_transition_triggered = true;
            }
        }
    }   

    // While in Run Control push joy messages onto the control message twist
    ctrl_msg.linear.x = joy_msg.linear.x;
    ctrl_msg.angular.z = joy_msg.angular.z;
}

void StateMachine::control_input_cb(const sensor_msgs::msg::Joy::SharedPtr msg)
{
    //TODO: Add a controller timout incase we drop control
    joy_msg.linear.x  = msg->axes[throttle_idx];
    joy_msg.angular.z = msg->axes[steer_idx];

    bool menu_pressed = msg->buttons[menu_idx] == 1;
    bool view_pressed = msg->buttons[view_idx] == 1;

    /** 
    RCLCPP_INFO(get_logger(), "Button states - Menu: %s, View: %s, Throttle: %.2f, Steer: %.2f",
        menu_pressed ? "PRESSED" : "RELEASED",
        view_pressed ? "PRESSED" : "RELEASED",
        joy_msg.linear.x,
        joy_msg.angular.z
    );
    **/

    // This lambda function deals with debouncing menu_pressed and view_pressed cleanly
    auto debounce_button = [&](bool is_pressed, bool& held_flag, rclcpp::Time& press_start_time, bool& triggered_flag)
    {
        if(is_pressed && !held_flag) {
            held_flag = true;
            press_start_time = this->now();
        } else if(!is_pressed && held_flag) {
            held_flag = false;
            triggered_flag = false;
        }
    };

    // Calling lambda ^^^ Look to use these values in the sm... 
    debounce_button(menu_pressed, menu_held, menu_pressed_start_time, menu_transition_triggered);
    debounce_button(view_pressed, view_held, view_pressed_start_time, view_transition_triggered);
}

void StateMachine::saurcon_state_cb(const std_msgs::msg::UInt8::SharedPtr msg)
{
    if(msg->data == static_cast<uint8_t>(SaurconRCState::STANDBY) ||
        msg->data == static_cast<uint8_t>(SaurconRCState::RUN_CONTROL) ||
        msg->data == static_cast<uint8_t>(SaurconRCState::RUN_AUTONOMOUS))    
    {
        saurcon_rc_ready = 1;
    } else {
        saurcon_rc_ready = 0;
    }

    //set heartbeat time    
    last_rc_heartbeat_ = this->now();
}

void StateMachine::check_heartbeat()
{
    if((this->now() - last_rc_heartbeat_) > rc_timeout_) {
        RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "RC heartbeat lost");

        if(current_state_ != SaurconState::STANDBY || current_state_ != SaurconState::STARTUP) {
            setState(SaurconState::STANDBY); //TODO: make this a fault.
        }
    }
}