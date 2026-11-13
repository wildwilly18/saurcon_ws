cmake_minimum_required(VERSION 3.8)
project(saurcon_nav)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
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
find_package(nav_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(Eigen3 REQUIRED)

# State estimator node
add_executable(state_estimator_node
  src/state_estimator_node.cpp
  src/state_estimator.cpp
)

ament_target_dependencies(state_estimator_node
  rclcpp
  std_msgs
  sensor_msgs
  geometry_msgs
  nav_msgs
  tf2_ros
)

target_link_libraries(state_estimator_node
  Eigen3::Eigen
)

target_include_directories(state_estimator_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
  $<INSTALL_INTERFACE:src>
)

install(TARGETS
  state_estimator_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/oak_depth.py DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  enable_testing()
  add_executable(test_dead_reckoning test/test_dead_reckoning.cpp src/state_estimator.cpp)
  target_include_directories(test_dead_reckoning PRIVATE src)
  target_link_libraries(test_dead_reckoning Eigen3::Eigen)
  add_test(NAME dead_reckoning COMMAND test_dead_reckoning)
  add_executable(test_map_odom test/test_map_odom.cpp)
  target_include_directories(test_map_odom PRIVATE src)
  add_test(NAME map_odom COMMAND test_map_odom)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  add_test(NAME launch_guards COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_launch_guards.py)
  add_test(NAME depth_model COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_depth.py)
endif()

ament_package()
