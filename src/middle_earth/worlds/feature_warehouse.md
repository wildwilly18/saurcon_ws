# Feature warehouse

A separate, tag-free world inspired by the warehouse classical cone-driving setup.
The 64.3 m asymmetric loop has three unequal lobes, changing-radius bends and
reverse-curvature transitions. It has 99 paired cone gates, 2.2 m apart.

Forty storage clusters supply different heights, offset stacked cartons, posts,
contrasting inset panels and geometric edges. Features extend down to camera
height. Irregular concrete repairs provide floor contrast. No ArUco/AprilTag
markers or fiducial textures are included. The original car model is referenced
without modifying its physics or frames.

All feature-cluster centres are at least 2.64 m from the sampled centreline;
clusters fit within a conservative 0.9 m horizontal radius, leaving more than
0.64 m beyond the nominal cone boundary. This is geometric validation, not a
claim that classical control or SLAM has passed a complete lap.

From the workspace root:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch saurcon_rc full_sim_saurcon.launch.py \
  world:=$PWD/src/middle_earth/worlds/feature_warehouse.world \
  use_aruco:=false slam:=true cone_follower:=true \
  follower_speed_limit:=1.5 database_path:=$PWD/maps/feature_warehouse.db
```

Hold View for two seconds in STANDBY to enable the classical driver. Start at a
conservative speed while evaluating this new course. Use a fresh database for
this environment. Existing maps from the stadium warehouse do not apply.

The world has a distinct name, `warehouse_irregular`. The evaluation tools read the
world name, spawn pose (start line and map origin) and centreline from the world file and
its `.track.json` sidecar (`scripts/sim_eval/world_info.py`, `saurcon_plan.track`), so lap
scoring, ground truth, the cone map's scoring and race videos work here as on the racetrack:

```bash
scripts/sim_eval/cone_race.sh fw_run 3 \
  world:=$PWD/src/middle_earth/worlds/feature_warehouse.world slam:=true cone_mapping:=rtab \
  database_path:=$PWD/maps/feature_warehouse.db
```

The sidecar is not an input to the classical controller, which drives from the camera alone.
Measured with the follower (2026-11-13, after its fixes for this track's dense 0.65 m gate
spacing; `docs/course/09_perception_driven_racing.md`, §7.5): 3-lap mapping, 29 loop
closures, 0.086 m RMS map error; two 3-lap localization runs, 0.068 and 0.077 m RMS.

Regenerate with `python3 src/middle_earth/scripts/build_feature_warehouse.py`
(requires NumPy, SciPy, Matplotlib and OpenCV). `feature_warehouse.png` is a generated
plan view, not an in-engine screenshot. See `docs/FEATURE_WAREHOUSE_VALIDATION.md` in the workspace for measured mapping,
localization, detector and reliability results after the texture revision.

## RGB-D surface revision

The generator now also writes committed PBR albedo textures under
`models/feature_warehouse_materials/textures`. Concrete uses irregular aggregate
and cracks; walls use masonry and area words; storage has unique worn grain and
stock labels. All textures are grayscale to avoid the cone detector color band.
Sun shadows and 0.38 ambient reveal depth edges. A non-colliding textured ceiling
and subdued background replace the white upper view; the ceiling does not cast
shadows, preserving sunlight on the cones. All original collisions, cone poses,
spawn and sidecar bytes are unchanged.
