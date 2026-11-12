# Saurcon Perception

ROS2 perception package for the Saurcon project. Includes ArUco marker detection using OpenCV and Eigen, configured for the markers used in the middle_earth simulation.

## Project Structure

```
saurcon_perception/
├── ARUCO_CONFIG.md               # ArUco marker specifications
├── CMakeLists.txt
├── package.xml
├── src/
│   ├── aruco_detector.hpp/.cpp   # Detector class (OpenCV, no ROS)
│   ├── aruco_detector_node.cpp   # ROS 2 node: image -> marker poses
│   ├── aruco_localizer_node.cpp  # ROS 2 node: marker poses -> vehicle pose in the map
│   ├── aruco_class_test.cpp      # Detector test on the images in data/test_images
│   └── aruco_test.cpp            # Standalone OpenCV test program
├── msg/                          # ArucoPose, ArucoPoseArray
├── launch/
│   └── aruco_detector.launch.py
└── config/
    ├── camera_params.json        # Intrinsics and camera mounting transform
    ├── marker_params.json        # Dictionary and marker size
    └── marker_map.csv            # World pose of every marker
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
ln -s /path/to/saurcon_perception src/saurcon_perception

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

### ROS2 Nodes

```bash
# Detector only
ros2 launch saurcon_perception aruco_detector.launch.py image_topic:=/camera/image

# Individual nodes
ros2 run saurcon_perception aruco_detector
ros2 run saurcon_perception aruco_localizer

# Detector test on the bundled images (works from any directory)
ros2 run saurcon_perception aruco_class_test
```

### Topics

| Node | Subscribes | Publishes |
| --- | --- | --- |
| `aruco_detector` | `/camera/image` (sensor_msgs/Image) | `/aruco_poses` (saurcon_perception/ArucoPoseArray), marker poses in the camera optical frame |
| `aruco_localizer` | `/aruco_poses` | `/saurcon/aruco_localization` (geometry_msgs/PoseWithCovarianceStamped), vehicle pose in the `map` frame, one message per marker |

### Parameters

`aruco_detector`:
- `camera_topic` (string, default `/camera/image`)
- `aruco_topic` (string, default `/aruco_poses`)
- `enable_whitelist_filter` (bool, default true): only report marker IDs listed in `marker_map.csv`
- `consecutive_frames_required` (int, default 2)

`aruco_localizer`:
- `aruco_topic`, `localization_topic`
- `camera_params`, `marker_map_csv`: paths to the config files
- `position_std` (m, default 0.1), `orientation_std` (rad, default 0.1): measurement noise for a nearby marker
- `noise_range_scale` (m, default 1.5): noise grows as `1 + (range / scale)^2`

Marker size and dictionary come from `config/marker_params.json`; camera
intrinsics and mounting from `config/camera_params.json`. They are not launch
parameters.

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
- Verify `marker_length` is the side of the black square, not of the plate it is printed on
- Ensure markers are flat and not distorted

**Build errors:**
- Install missing dependencies: `rosdep install --from-paths src --ignore-src -y`
- Source ROS2: `source /opt/ros/jazzy/setup.bash`

## License

MIT
