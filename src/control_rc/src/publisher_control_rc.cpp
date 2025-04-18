#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "std_msgs/msg/float64.hpp"


using namespace std::chrono_literals;

/* This example creates a subclass of Node and uses a fancy C++11 lambda
* function to shorten the callback syntax, at the expense of making the
* code somewhat more difficult to understand at first glance. */

class ControlPublisher : public rclcpp::Node
{
public:
  ControlPublisher()
  : Node("control_rc"), count_(0)
  {
    throttle_publisher_ = this->create_publisher<std_msgs::msg::Float64>("throttle", 10);
    auto timer_callback =
      [this]() -> void {
        auto message = std_msgs::msg::Float64();
        message.data = 0.5;
        RCLCPP_INFO(this->get_logger(), "Publishing: '%1.2f'", message.data);
        this->throttle_publisher_->publish(message);
      };
    timer_ = this->create_wall_timer(500ms, timer_callback);
  }

private:
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr throttle_publisher_;
  size_t count_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ControlPublisher>());
  rclcpp::shutdown();
  return 0;
}