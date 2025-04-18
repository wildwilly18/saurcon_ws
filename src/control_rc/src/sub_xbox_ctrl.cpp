#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"
#include "std_msgs/msg/float32.hpp"
#include "geometry_msgs/msg/twist.hpp"

using namespace std;
size_t throttle_idx = 1;
size_t steer_idx = 3;
float throttle = 0.0;
float steer = 0.0;

class JoySubToCMD : public rclcpp::Node
{
public:
  JoySubToCMD()
  : Node("JoyToCMD")
  {
    subscription_ = this->create_subscription<sensor_msgs::msg::Joy>(
      "/joy", 10,
      bind(&JoySubToCMD::joy_callback, this, placeholders::_1)
    );


    // Publish VEL STEER 
    publisher_ = this->create_publisher<geometry_msgs::msg::Twist>(
        "/ctrl_output",
        10
    );

    RCLCPP_INFO(this->get_logger(), "Joy to CMD Node Started");

    }

private:
  void joy_callback(const sensor_msgs::msg::Joy::SharedPtr msg)
  {
    auto twist_msg = geometry_msgs::msg::Twist();

    twist_msg.linear.x = msg->axes[throttle_idx];
    twist_msg.angular.z = msg->axes[steer_idx];
    publisher_->publish(twist_msg);
    RCLCPP_INFO(this->get_logger(), "Published CMD: linear.x=%.2f angular.z=%.2f",
    twist_msg.linear.x, twist_msg.angular.z);
  }

  rclcpp::Subscription<sensor_msgs::msg::Joy>::SharedPtr subscription_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(make_shared<JoySubToCMD>());
  rclcpp::shutdown();
  return 0;
}
