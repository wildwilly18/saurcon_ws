# saurcon_plan — planning for the SAURCON car

Drives the car around a cone track from what its camera sees, with the classical cone
follower. No map, no localization and no learning are needed; RTAB-Map may run alongside
it to build a map.

```
OAK-D RGB + depth ─► cone_follower_node: ConeDetector ─► ConeMemory (odom frame) ─► ConeFollower ─► /auto_cmd
                         ▲ TF odom→base_link and /saurcon/odom_nav (odometry UKF)          ─► state machine (RUN_AUTONOMOUS)
```

## Modules

| File | Purpose | Needs ROS |
|---|---|---|
| `saurcon_plan/vehicle.py` | Car parameters (wheelbase, steering limit, control rate) and the servo slew limit | no |
| `saurcon_plan/track.py` | Track centreline and cone gates read from a world file (and its `.track.json` sidecar) | no |
| `saurcon_plan/cones.py` | Cone detector: colour, blobs, depth / ground-plane / size ranging; cone map and scoring | no |
| `saurcon_plan/memory.py` | Short-term cone memory in a frame that does not move with the car | no |
| `saurcon_plan/cone_follower.py` | Classical follower: gate midpoints from a Delaunay triangulation, chained into a path; single-boundary fallback; pure pursuit; curvature speed profile | no |
| `saurcon_plan/cone_follower_node.py` | ROS 2 node `cone_follower`: camera and odometry in, `/auto_cmd` out; stops on stale inputs | yes |
| `saurcon_plan/cone_mapper_node.py` | ROS 2 node `cone_mapper`: cone map in the map frame from RTAB-Map or ground-truth poses | yes |

The core modules need only NumPy, SciPy and OpenCV, so the MuJoCo simulation (`saurcon_rl`)
uses the same detector, memory and follower as the car.

## Use

```bash
source /opt/ros/jazzy/setup.bash && source install/setup.bash
# Gazebo, camera-only driving (hold the controller's view button 2 s for RUN_AUTONOMOUS)
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false cone_follower:=true
# ... with RTAB-Map mapping and a cone map
ros2 launch saurcon_rc full_sim_saurcon.launch.py use_aruco:=false slam:=true \
    cone_follower:=true cone_mapping:=rtab
# Scripted 3-lap race with logs, chase camera and the follower's waypoints, then a video
scripts/sim_eval/cone_race.sh my_run 3
.venv-rl/bin/python scripts/sim_eval/make_race_video.py evaluation/cones_gz/my_run my_run.mp4
```

Launch arguments: `cone_follower:=true` starts the node; `follower_speed_limit` caps the
speed command (the follower itself plans at most 5 m/s); `cone_debug_csv:=<file>` logs the
follower's state (pose, path, cones) every step, which `make_race_video.py` draws as
waypoints.

Node parameters (defaults): `latency` 0.05 s (pose predicted this far ahead before steering),
`memory_s` 5 s (how long a cone is remembered), `image_timeout` 0.3 s, `odom_timeout` 0.25 s,
`tf_timeout` 0.25 s, `tf_fallback_max` 0.1 s, `hsv_lo`/`hsv_hi` (detector colour band),
`camera_height` 0.137 m.

**Safety.** The node publishes a zero command and resets its state whenever the newest image
was captured more than 0.3 s ago, odometry is older than 0.25 s, or the `odom → base_link`
transform is missing or older than 0.25 s; a missing transform also clears the cone memory.
Each colour image is paired with the depth image of the same stamp and with the odometry pose
at that stamp.

Results (Gazebo, RTAB-Map running, no markers): racetrack 3 laps in 12.5–13.7 s; feature
warehouse 3-lap mapping and two 3-lap localization runs, 17.7–18.6 s per lap. The design, the
failures found while building it and the comparison with learned policies are in
`docs/course/09_perception_driven_racing.md`, §7–8.

## Tests

```bash
source /opt/ros/jazzy/setup.bash
PYTHONPATH=src/saurcon_plan:$PYTHONPATH python3 -m pytest -q src/saurcon_plan/test
```

`test_cone_follower.py`: path geometry, curvature, and two real failing frames (boundary
chords in dense gates). `test_follower_node.py`: the stale-input rules with a fake clock, TF
buffer and publisher (nothing is actuated).
