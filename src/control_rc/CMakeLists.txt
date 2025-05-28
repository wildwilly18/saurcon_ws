cmake_minimum_required(VERSION 3.8)
project(control_rc)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)


add_executable(talker src/publisher_control_rc.cpp)
add_executable(ctrl_interface src/ctrl_interface.cpp)
add_executable(saurcon_main src/saurcon.cpp src/state_machine.cpp)
ament_target_dependencies(talker rclcpp std_msgs)
ament_target_dependencies(ctrl_interface rclcpp sensor_msgs geometry_msgs)
ament_target_dependencies(saurcon_main rclcpp sensor_msgs geometry_msgs std_msgs)

# find headers
target_include_directories(saurcon_main PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

install(TARGETS
  talker
  ctrl_interface
  saurcon_main
  DESTINATION lib/${PROJECT_NAME})

install(
  DIRECTORY include/
  DESTINATION include
)
  # Install the launch directory
install(DIRECTORY launch
DESTINATION share/${PROJECT_NAME}
)

ament_package()
