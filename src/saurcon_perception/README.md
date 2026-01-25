# Saurcon Perception

ROS2 perception package for the Saurcon project. Includes ArUco marker detection using OpenCV and Eigen, configured for the markers used in the middle_earth simulation.

## Project Structure

```
saurcon_perception/
├── ARUCO_CONFIG.md              # ArUco marker specifications
├── README.md                    # This file
├── CMakeLists.txt              # Build configuration
├── package.xml                 # ROS2 package metadata
├── include/
│   └── aruco_detector/
│       └── aruco_detector.hpp  # Detector class header
├── src/
│   ├── aruco_detector.cpp      # Detector implementation
│   ├── aruco_detector_node.cpp # ROS2 node wrapper
│   └── aruco_test.cpp          # Standalone test program
├── launch/
│   └── aruco_detector.launch.py # Launch file
└── config/
    └── aruco_params.yaml       # Configuration parameters
```

## Features

- **ArUco Detection**: Detect DICT_4X4_50 markers (IDs 0-19)
- **Pose Estimation**: Calculate 6-DOF pose using OpenCV
- **Eigen Integration**: Rotation matrices and quaternions with Eigen
- **ROS2 Node**: Full ROS2 integration with topics and visualization
- **Standalone Testing**: Test program without ROS2 dependencies

## Dependencies

- **ROS2** (Humble or later)
- **OpenCV** (with ArUco module)
- **Eigen3**
- **cv_bridge**
- **tf2**

## Building

### As ROS2 Package

```bash
# Navigate to your ROS2 workspace
cd ~/your_ros2_ws

# Copy or symlink this package to src/
ln -s /home/wilson/saurcon_perception src/saurcon_perception

# Build
colcon build --packages-select saurcon_perception

# Source
source install/setup.bash
```

### Standalone Test Program

The standalone test program (`aruco_test`) is automatically built with the package and doesn't require ROS2 to run.

## Usage

### Standalone Test Program

```bash
# Generate a test marker
./build/saurcon_perception/aruco_test

# Test with webcam
./build/saurcon_perception/aruco_test webcam

# Test with image file
./build/saurcon_perception/aruco_test image path/to/image.jpg
```

### ROS2 Node

```bash
# Launch with default parameters
ros2 launch saurcon_perception aruco_detector.launch.py

# Launch with custom parameters
ros2 launch saurcon_perception aruco_detector.launch.py \
    marker_size:=0.1524 \
    camera_frame:=camera_link \
    image_topic:=/camera/image_raw \
    camera_info_topic:=/camera/camera_info
```

### Topics

**Subscribed:**
- `image_raw` (sensor_msgs/Image): Input camera image
- `camera_info` (sensor_msgs/CameraInfo): Camera calibration

**Published:**
- `aruco_poses` (geometry_msgs/PoseArray): Detected marker poses
- `aruco_debug_image` (sensor_msgs/Image): Annotated image with detections
- `aruco_markers_viz` (visualization_msgs/MarkerArray): RViz visualization markers

### Parameters

- `marker_size` (double, default: 0.1524): Physical marker size in meters
- `dictionary_id` (int, default: 4): ArUco dictionary (4 = DICT_4X4_50)
- `camera_frame` (string, default: "camera_link"): Camera frame ID
- `publish_visualization` (bool, default: true): Enable RViz markers
- `min_marker_id` (int, default: 0): Minimum valid marker ID
- `max_marker_id` (int, default: 19): Maximum valid marker ID

## API Reference

### ArucoDetector Class

```cpp
#include "aruco_detector/aruco_detector.hpp"

// Create detector
aruco_detector::ArucoDetector detector(cv::aruco::DICT_4X4_50, 0.1524);

// Detect markers
auto markers = detector.detectMarkers(image, camera_matrix, dist_coeffs);

// Access results
for (const auto& marker : markers) {
    int id = marker.id;
    Eigen::Vector3d position = marker.translation;
    Eigen::Quaterniond orientation = marker.quaternion;
    Eigen::Matrix3d rotation = marker.rotation;
}
```

## Configuration

See `ARUCO_CONFIG.md` for detailed marker specifications from the middle_earth simulation.

## Next Steps

1. **Test standalone program**: Verify detection with webcam or test images
2. **Integrate with ROS2**: Connect to your camera topics
3. **Calibrate camera**: Get accurate camera matrix and distortion coefficients
4. **Tune parameters**: Adjust detection parameters in config file if needed
5. **Add features**: Extend with tracking, filtering, or custom services

## Troubleshooting

**No markers detected:**
- Check camera calibration
- Verify marker size parameter
- Ensure good lighting
- Confirm marker dictionary matches (DICT_4X4_50)

**Poor pose estimation:**
- Calibrate camera properly
- Verify marker size is correct (0.1524m = 6 inches)
- Ensure markers are flat and not distorted

**Build errors:**
- Install missing dependencies: `sudo apt install ros-humble-cv-bridge libopencv-dev libeigen3-dev`
- Source ROS2: `source /opt/ros/humble/setup.bash`

## License

MIT
