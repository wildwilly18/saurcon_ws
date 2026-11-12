# OAK-D Lite simulation contract

This is a selectable-driver-profile approximation, not a calibrated digital twin.
Camera poses follow Luxonis' generic OAK-D description (RGB at device origin,
left/right ±37.5 mm along Y). Device-specific calibration should replace these
on hardware. The body is 91 × 28 × 17.5 mm and total model mass is 61 g.

| ROS topic | Type / encoding | Profile | Frame |
|---|---|---|---|
| `/oak/rgb/image_raw` | sensor_msgs/Image, rgb8 | 640×400, 15 Hz, 1.204 rad horizontal FOV | oak_rgb_camera_optical_frame |
| `/oak/rgb/camera_info` | sensor_msgs/CameraInfo | fx=fy≈465.74; cx=320, cy=200 | same |
| `/oak/stereo/image_raw` | sensor_msgs/Image, 16UC1 millimetres, zero invalid | RGB-aligned, 640×400, 15 Hz, accepted range 0.2–4 m | same |
| `/oak/stereo/camera_info` | sensor_msgs/CameraInfo | RGB intrinsics | same |
| `/oak/left/image_raw`, `/oak/right/image_raw` | sensor_msgs/Image, mono8 | 640×480, 15 Hz, 73° horizontal FOV | oak_left/right_camera_optical_frame |
| `/oak/left/camera_info`, `/oak/right/camera_info` | sensor_msgs/CameraInfo | 75 mm baseline; right P[3] = −fx×0.075 | same |
| `/oak/imu/data` | sensor_msgs/Imu | 100 Hz | oak_imu_frame |

Native hardware has an IMX214 rolling-shutter colour sensor (13 MP) and OV7251
640×480 global-shutter mono sensors. The selected 15 Hz rate is a configuration,
not a hardware limit. RGB output here is an idealized crop/downscale with legacy
640×400 calibration, retained for controlled ArUco comparisons; it is not claimed
to reproduce a particular factory RGB crop. Depth operating range depends on
stereo settings, texture and light; 0.2–4 m is our simulation cutoff, not a
universal device specification. This user's unit has BMI270; early Lite units
may have no IMU. The 100 Hz combined simulated IMU stream is a chosen output
profile, not a claim that the hardware accel/gyro sample synchronously at 100 Hz.

TF: base_link → oak → each camera frame → optical frame, plus oak_imu_frame.
Legacy camera_link and camera_optical_frame are aliases at the RGB sensor pose.
Legacy `/camera/image`, `/camera/camera_info`, `/camera/depth_image` remain.
Depth legacy output now uses 16UC1, not the old 32FC1 encoding.

`oak_depth.py` synchronizes rendered RGB and depth by exact capture stamp and
applies sigma_z = z² × 0.25 pixels / (432 pixels × 0.075 m). Local smoothed
contrast below 2 intensity levels causes invalid depth. Seed, disparity noise,
range limits and texture threshold are ROS parameters. These are explicit
engineering assumptions, not measured OAK noise calibration. Image noise is
Gaussian stddev 0.007 of full scale; IMU noise is 0.002 rad/s and 0.02 m/s².

Not modelled: actual stereo matching, occlusion holes between camera viewpoints,
left/right calibration error, distortion, exposure, rolling shutter, lighting-
dependent noise, temperature drift, USB latency, device clock drift, neural
network outputs. RGBD rendering gives perfect geometric registration before
noise. Low-texture rejection uses aligned RGB contrast, not the mono pair.
IMU location/orientation is assumed at device origin in body axes: the upstream
Humble generic Lite description has no IMU transform. Hardware calibration is
required before claiming an exact IMU frame match. The real car's existing IMU
continues to drive navigation.

Sources checked 2026-11-12:

- [Luxonis product specifications](https://checkout.luxonis.com/products/oak-d-lite-1)
- [Luxonis driver documentation](https://docs.luxonis.com/software-v3/depthai/ros/driver)
- [Generic camera frames](https://github.com/luxonis/depthai-ros/blob/887248d72cc6b9515793f828645346408b9cad47/depthai_descriptions/urdf/include/depthai_macro.urdf.xacro)
- [Depth topic/alignment implementation](https://github.com/luxonis/depthai-ros/blob/887248d72cc6b9515793f828645346408b9cad47/depthai_ros_driver/src/dai_nodes/sensors/stereo.cpp)
- [Image/depth encoding conversion](https://github.com/luxonis/depthai-ros/blob/887248d72cc6b9515793f828645346408b9cad47/depthai_bridge/src/ImageConverter.cpp)

The inspected driver commit is on Humble; a Jazzy real-driver configuration and
actual device calibration remain part of deferred hardware integration.

`config/depthai_reference.yaml` records a reference v2 driver profile matching
the requested output sizes/rates. It has not been run on this user's camera;
crop intrinsics, IMU rates and calibration must be checked on hardware. It is
not automatically loaded by simulation or claimed as a validated Jazzy setup.
