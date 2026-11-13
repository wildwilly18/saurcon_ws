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
  use_aruco:=false slam:=true cone_policy_model:=classical \
  policy_speed_limit:=1.5 database_path:=$PWD/maps/feature_warehouse.db
```

Hold View for two seconds in STANDBY to enable the classical driver. Start at a
conservative speed while evaluating this new course. Use a fresh database for
this environment. Existing maps from the stadium warehouse do not apply.

The world has a distinct name, `warehouse_irregular`. Existing evaluation tools
that hard-code `warehouse_racetrack`, its start line, or its centreline must be
adapted before using them for lap scoring or truth overlays. The ordinary ROS
launch and camera-based classical follower do not require those scoring tools.
The world-aware evaluation-tool changes in the working tree supply this support;
they are owned by a separate session and are not included in the texture-fix commit.
The `.track.json` sidecar supplies the course geometry and spawn pose for that
integration; it is not an input to the classical controller.

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
