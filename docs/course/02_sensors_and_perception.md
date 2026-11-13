# Chapter 2 — Sensors and Perception

**Notebook:** [02_camera_geometry_and_pnp.ipynb](notebooks/02_camera_geometry_and_pnp.ipynb)

## Learning objectives

- Model wheel odometry and gyroscope errors, and explain why they drift.
- Project 3-D points with the pinhole model; convert between field of view and focal length.
- Derive stereo depth and its error growth with range.
- Recover a marker's pose with PnP, and recognise the planar pose ambiguity.
- Explain camera vs. optical frames and why the distinction causes bugs.

## 1. Proprioceptive sensors

**Wheel odometry.** Speed is $v = r\,\omega$ averaged over the driven wheels. Errors
come from wheel radius (a 1% radius error is a 1% distance error), slip under
acceleration and cornering, and quantisation. In SAURCON the ESP32 publishes speed
and steering angle on `/saurcon/odom`; in simulation `sim_saurcon_rc` computes it
from Gazebo joint states.

**Gyroscope.** A MEMS gyro measures $\omega_\text{meas} = \omega + b + n$, with a
slowly varying **bias** $b$ and white noise $n$ (standard deviation $\sigma_n$ per
sample). Integrated heading error grows as

$$\delta\psi(t) = b\,t + \text{random walk with } \sigma\sqrt{t\,\Delta t}.$$

The bias term dominates: an uncorrected bias of only 0.001 rad/s is 12° after
200 s. If you estimate the bias by averaging $N$ stationary samples, the estimate
itself has error $\sigma_n/\sqrt N$ — this exact effect is the case study in
chapter 3.

## 2. The pinhole camera

A point $(X, Y, Z)$ in the **optical frame** (x right, y down, z forward) projects to
pixel

$$u = f_x \frac{X}{Z} + c_x, \qquad v = f_y \frac{Y}{Z} + c_y.$$

For an image $W$ pixels wide with horizontal field of view $\theta$,
$f_x = \dfrac{W/2}{\tan(\theta/2)}$. SAURCON's simulated camera is 640 px wide with
$\theta = 1.204$ rad, so $f_x = 465.7$ px. (A configuration file once said 929.4 —
consistent with a different resolution, not this camera. Always derive intrinsics
from the actual stream.)

**Camera frame vs. optical frame.** ROS body frames are x forward, y left, z up.
Optical frames are x right, y down, z forward. The rotation between them is fixed;
forgetting it is the most common perception bug, and it produces poses that look
"almost right but rotated 90°".

## 3. Stereo depth

Two cameras a **baseline** $B$ apart see a point at disparity $d = u_L - u_R$
pixels. Depth is

$$Z = \frac{f B}{d}, \qquad \frac{\partial Z}{\partial d} = -\frac{Z^2}{f B}.$$

So a fixed disparity error $\sigma_d$ gives a depth error that grows with the
**square** of range: $\sigma_Z \approx Z^2 \sigma_d / (f B)$. The OAK-D Lite has a
75 mm baseline; with $f \approx 450$ px and $\sigma_d = 0.1$ px the error is 1 mm at
0.5 m but 5 cm at 5 m. Passive stereo also fails on surfaces without texture (no
features to match), returning zero (invalid) depth. The simulated OAK-D model
reproduces both effects in `src/saurcon_nav/scripts/oak_depth.py`.

## 4. Fiducials and PnP

An ArUco marker is a square of known side $s$ with a binary code. Detection finds
its four corners in the image; **Perspective-n-Point (PnP)** finds the rotation $R$
and translation $t$ of the marker in the camera frame that best reproject the known
3-D corners onto them:

$$\min_{R,t} \sum_{i=1}^{4} \left\| \pi\!\left(K (R\,P_i + t)\right) - p_i \right\|^2.$$

For a single planar square, OpenCV's `SOLVEPNP_IPPE_SQUARE` solver is designed for
this case and returns **two** solutions. When the marker is small or viewed
head-on, the two have nearly equal reprojection error but orientations mirrored
about the line of sight. Picking the wrong one moves the inferred *vehicle* position
sideways by roughly range × orientation error.

Given the marker's world pose $T_{wm}$ (from a surveyed map), the vehicle pose is

$$T_{wv} = T_{wm}\, (T_{vc}\, T_{cm})^{-1},$$

where $T_{vc}$ is the camera mounting transform and $T_{cm}$ the PnP result.

## 5. Case studies

**The marker map that was 180° off.** Markers 3 and 10 sat across the track
ends; the map gave their facing direction with the wrong sign. Seen from the
correct side, the localizer placed the car mirrored through the marker, 3.6 m away
with heading reversed. Found by teleporting the car in front of each marker and
comparing to ground truth — a test worth automating for any map.

**Wrong marker size.** The texture has a 10% white margin, so the black square is
0.122 m, not the 0.1524 m plate. At close range the detector locked onto the plate
edge (which matched 0.1524 m) and range was right; further away it locked onto the
real square and range was 12–21% long. Two errors cancelling in one regime is a
classic trap.

**Ambiguous poses.** Once the filter actually trusted marker fixes, ambiguous PnP
solutions made the estimate jump by up to 1.6 m. The fix rejects detections whose
two solutions disagree by more than 15° and are nearly equally good, and inflates
measurement noise as $1 + (\text{range}/1.5\,\text{m})^2$ — the same square law as
stereo.

## How SAURCON does it

| Concept | Where |
|---|---|
| OAK-D Lite simulated device | `src/middle_earth/models/oak_d_lite/` (README lists modelling gaps) |
| Depth post-processing | `src/saurcon_nav/scripts/oak_depth.py` |
| ArUco detection + PnP | `src/saurcon_perception/src/aruco_detector.cpp` |
| Marker → vehicle pose | `src/saurcon_perception/src/aruco_localizer_node.cpp` |

## Exercises

1. ★ Compute $f_x$ for a 1280-px-wide stream with the same FOV. What happens to depth error?
2. ★ In the notebook, project a 0.122 m marker at 1, 3 and 5 m; how many pixels wide is it?
3. ★★ Show that for $T_{wv} = T_{wm}(T_{vc}T_{cm})^{-1}$, a yaw error $\epsilon$ in $T_{cm}$ moves the vehicle laterally by about range × $\epsilon$.
4. ★★ Reproduce the IPPE ambiguity in the notebook: at what range do the two solutions' errors become indistinguishable with 0.3 px corner noise?
5. ★★★ The OAK-D Lite computes depth aligned to the colour camera. Write the transform chain needed to align depth computed in the left mono camera to the colour image.
