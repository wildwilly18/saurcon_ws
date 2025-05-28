#include "rclcpp/rclcpp.hpp"
#include "control_rc/state_machine.hpp"

//Call State Machine for Saurcon
int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<StateMachine>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}