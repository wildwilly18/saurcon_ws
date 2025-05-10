#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "std_msgs/msg/float32.hpp"
#include "geometry_msgs/msg/twist.hpp"

using namespace std;
size_t throttle_idx = 1;
size_t steer_idx = 3;
float throttle = 0.0;
float steer = 0.0;

class CTRL_INTERFACE : public rclcpp::Node
{
public:
  CTRL_INTERFACE()
  : Node("ControlInterface")
  {
    subscription_joy = this->create_subscription<sensor_msgs::msg::Joy>(
      "/joy", 10,
      bind(&CTRL_INTERFACE::joy_callback, this, placeholders::_1)
    );

    // Publish VEL STEER 
    publisher_ctrl = this->create_publisher<geometry_msgs::msg::Twist>(
        "/ctrl_output",
        10
    );

    RCLCPP_INFO(this->get_logger(), "Control Interface Started");

    }

private:
  void joy_callback(const sensor_msgs::msg::Joy::SharedPtr msg)
  {
    auto twist_msg = geometry_msgs::msg::Twist();

    twist_msg.linear.x = msg->axes[throttle_idx];
    twist_msg.angular.z = msg->axes[steer_idx];
    publisher_ctrl->publish(twist_msg);
    RCLCPP_INFO(this->get_logger(), "Published CMD: linear.x=%.2f angular.z=%.2f",
    twist_msg.linear.x, twist_msg.angular.z);
  }

  rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr subscription_joy;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_ctrl;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(make_shared<CTRL_INTERFACE>());
  rclcpp::shutdown();
  return 0;
}
