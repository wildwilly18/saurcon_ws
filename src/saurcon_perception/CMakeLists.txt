cmake_minimum_required(VERSION 3.8)
project(saurcon_perception)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

# Find OpenCV (for ArUco detection)
find_package(OpenCV REQUIRED)

# Find Eigen3
find_package(Eigen3 REQUIRED)

# Find Boost
find_package(Boost REQUIRED COMPONENTS json)

# Include directories
include_directories(
  include
  ${OpenCV_INCLUDE_DIRS}
  ${EIGEN3_INCLUDE_DIR}
  ${Boost_INCLUDE_DIRS}
)

# Add aruco_test executable
add_executable(aruco_test
  src/aruco_test.cpp
)

target_link_libraries(aruco_test
  ${OpenCV_LIBS}
)

# Copy executable to workspace root after building
add_custom_command(TARGET aruco_test POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy
  $<TARGET_FILE:aruco_test>
  ${CMAKE_SOURCE_DIR}/aruco_test.exe
  COMMENT "Copying aruco_test to workspace root"
)

# Install aruco_test executable
install(TARGETS aruco_test
  DESTINATION lib/${PROJECT_NAME}
)

# Add aruco_class_test executable
add_executable(aruco_class_test
  src/aruco_class_test.cpp
  src/aruco_detector.cpp
)

target_link_libraries(aruco_class_test
  ${OpenCV_LIBS}
  ${Boost_LIBRARIES}
  Eigen3::Eigen
)

# Copy executable to workspace root after building
add_custom_command(TARGET aruco_class_test POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy
  $<TARGET_FILE:aruco_class_test>
  ${CMAKE_SOURCE_DIR}/aruco_class_test.exe
  COMMENT "Copying aruco_class_test to workspace root"
)

# Install aruco_class_test executable
install(TARGETS aruco_class_test
  DESTINATION lib/${PROJECT_NAME}
)

# Install header files
install(DIRECTORY include/
  DESTINATION include/
)

# Install launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/
)

# Install config files
install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
