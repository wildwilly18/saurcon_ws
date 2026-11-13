# Feature warehouse materials

These committed grayscale PNG albedo maps are generated deterministically by
`../../scripts/build_feature_warehouse.py`. No network assets or encoded visual
markers are used. Concrete aggregate, irregular cracks, wear, grain, masonry
seams and ordinary stock/area words provide image features at multiple scales.
Each of the 40 storage textures and four wall textures has its own RNG seed;
texture RNG streams never consume the course-generation RNG.

The world uses PBR metal-workflow materials with zero metalness and 0.9 roughness.
Gazebo resolves `model://feature_warehouse_materials/textures/...` through the
existing model resource path. The directory supplies textures, not a spawnable
model. All generated texels are achromatic: none passes the cone detector's
saturated orange/yellow HSV threshold. See the validation report for the rendered
frame audit, which also checks lighting and existing colored objects.
