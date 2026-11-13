# RTAB-Map simulation

Build after running `scripts/setup.sh` (which now installs RTAB-Map):

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select saurcon_nav saurcon_rc
source install/setup.bash
export SAURCON_WS="$PWD"
```

Run mapping (new database filename avoids overwriting an earlier map):

```bash
ros2 launch saurcon_rc full_sim_saurcon.launch.py \
  headless:=true record:=false use_aruco:=false slam:=true \
  database_path:="$PWD/maps/warehouse.db"
```

Stop cleanly with Ctrl-C to save the database. Run localization using that map:

```bash
ros2 launch saurcon_rc full_sim_saurcon.launch.py \
  headless:=true record:=false use_aruco:=false slam:=true \
  mode:=localization database_path:="$PWD/maps/warehouse.db"
```

`reset_database:=true` explicitly erases the selected database for fresh mapping.
It is rejected in localization mode, as is a missing localization database.
The default launch keeps ArUco enabled for comparison. SLAM requires
`use_aruco:=false`; incompatible selections fail before starting the simulator.
To test only dead reckoning use `use_aruco:=false slam:=false`.

Frame ownership with `slam:=true` (default `fuse_slam:=true`): two instances of the
wheel/gyro UKF run.

- `state_estimator` (odometry only) publishes TF `odom -> base_link`,
  `/saurcon/odom_nav` and `/saurcon/nav_state_odom`. RTAB-Map reads this
  odometry from TF. It never sees RTAB-Map's corrections, which avoids a
  feedback loop.
- `state_estimator_global` runs the same prediction and fuses RTAB-Map's pose
  as a measurement: `/rtabmap/localization_pose` in localization mode, the
  newest node of `/rtabmap/mapPath` in mapping mode (RTAB-Map publishes no
  localization pose while mapping). Each fix is shifted from its camera
  timestamp to the present using the odometry travelled since. Measurement
  noise floors: 0.05 m and 0.005 rad. It publishes `/saurcon/nav_state`
  (map frame, 50 Hz) and TF `map -> odom`; RTAB-Map's own `map -> odom`
  publishing is turned off.

`map -> odom` is composed from the global pose and the `odom -> base_link`
transform **at the same instant**: the global filter keeps one second of its poses
and interpolates them to the stamp of the newest odometry transform
(`src/saurcon_nav/src/map_odom.hpp`); if that stamp is outside the history, no
correction is published that tick.

Global consumers read `/saurcon/nav_state` or TF `map -> base_link`; controllers
that need jump-free motion use `odom`. `/map` is the 2-D occupancy grid (5 cm
cells, depth out to `Grid/RangeMax` 4 m). `Grid/RayTracing` is on, so each depth
ray clears the cells between the camera and what it hit, and the cells under the
car's path are marked free (`Grid/Footprint*`, `GridGlobal/FootprintRadius`).
Without ray tracing about half the track area stayed unknown after four laps; with
it 11–14% does. It costs CPU: the cone node's camera rate fell from ~11 to ~9.5
frames/s with RTAB-Map running. Validate on real stereo depth before relying on it
on the car.
`fuse_slam:=false` restores RTAB-Map publishing `map -> odom` itself with no
global UKF. With ArUco (`use_aruco:=true`) there is one instance, fusing ArUco
in the map frame as before.
The RTAB-Map-only launch is `ros2 launch saurcon_nav rtabmap_sim.launch.py`;
provide the simulator/sensors/odometry separately when using it.

## Evaluation

```bash
# Output directory must not exist. LAPS defaults to one.
LAPS=2 bash scripts/sim_eval/runsim.sh "$PWD" /tmp/warehouse-mapping \
  use_aruco:=false slam:=true database_path:="$PWD/maps/warehouse.db"
python3 scripts/sim_eval/analyze.py /tmp/warehouse-mapping \
  --kind map --align --duration 100 --video --output evaluation/mapping
python3 scripts/sim_eval/analyze.py /tmp/warehouse-mapping \
  --kind nav --align --duration 100 --output evaluation/odometry
```

The harness uses a workspace lock and only terminates its own process groups.
Each run contains timestamped poses, camera frames, driver/launch logs, latest
occupancy image/metadata and accepted loop closures when present. Analyzer
supports any number of runs, plots and JSON metrics, and optional annotated
camera video. `analyze_legacy.py` preserves the original comparison renderer;
its fixed run-directory assumptions are obsolete.

`--align` applies one initial SE(2) transform, never a trajectory fit. It is
appropriate for mapping/odometry whose origin is the start pose. Localization
in an existing map needs the **mapping run's fixed map-to-world alignment**
for absolute accuracy comparisons (`--alignment-from /tmp/warehouse-mapping`); independently aligning localization can
hide an initial localization offset. Inspect coverage/scored duration and
ensure the driver completed the requested lap. `scored_duration_s` is the
first-to-last sample span; `largest_gap_s` and `observed_duration_s` (sum of
intervals no longer than 0.25 seconds) expose tracking dropouts within it. Baseline measurements used
wall receipt times; current logs preserve Gazebo capture timestamps through
`gt_bridge.py` using the Harmonic Python transport supplied by ROS vendor
packages. The bridge selects the vehicle by name rather than array position.
Each run sets a unique `GZ_PARTITION` and defaults to `ROS_DOMAIN_ID=42`;
source its `environment.txt` and export both variables to inspect a live run.
Only the runner owns the evaluation lock; child processes do not inherit it.


Generate additional scenarios without changing the original world:

```bash
python3 scripts/sim_eval/make_world.py /tmp/no-markers.world --no-markers
python3 scripts/sim_eval/make_world.py /tmp/reverse.world --yaw 3.141592653589793
REVERSE=1 bash scripts/sim_eval/runsim.sh "$PWD" /tmp/reverse-run \
  world:=/tmp/reverse.world use_aruco:=false slam:=true mode:=localization \
  database_path:="$PWD/maps/warehouse.db"
```

Use `--x`/`--y` for alternative starts and pass the generated `world:=...`.
In localization mode, give a known start pose with
`initial_pose:="x y z roll pitch yaw"` in the map frame (the map origin is the
rear-axle pose where mapping started). For the reverse world that is
`initial_pose:="0.254 0 0 0 0 3.14159"`. Without it RTAB-Map relocalizes
globally, which can lock onto a look-alike place while the car is parked.
The controller starts at the nearest path sample. Keep starts on the track.

## Validation and limitations

Run `colcon test --packages-select saurcon_nav` for dead-reckoning and depth
regressions. While a run is active, source/export its environment and run
`python3 scripts/sim_eval/check_sensors.py`. For independent wall fixtures:

```bash
for distance in 0.5 1 2 4; do
  python3 scripts/sim_eval/check_wall_depth.py "$distance"
done
```

These use separate Gazebo partitions and the actual OAK model. They verify
rendered depth geometry; the depth unit tests separately check range rejection,
millimetre conversion, blank-surface rejection and quadratic noise scaling.
See [RTABMAP_STATUS.md](RTABMAP_STATUS.md) for actual run results
and [sensor contract](../src/middle_earth/models/oak_d_lite/README.md) for all
sensor assumptions. The model does not reproduce actual stereo matching or
calibrated hardware noise. No physical vehicle validation is claimed.

## Visual-odometry fallback

For an explicit comparison, add `visual_odometry:=true` with `slam:=true
use_aruco:=false`. This starts `rtabmap_odom/rgbd_odometry`, disables the wheel
estimator to avoid competing TF publishers, and feeds its `/saurcon/nav_state`
odometry into RTAB-Map. It is not the default: passive depth and repetitive
low-texture views can make visual tracking fail. Use a fresh database and score
both pose coverage and error; a short surviving segment is not a successful lap.

The driver intentionally tests joystick loss after each lap, so a controller
FAULT near the end of its log is expected. Scoring should cover the driving
window, not the subsequent watchdog exercise.
