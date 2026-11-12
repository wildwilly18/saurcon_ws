# ArUco Marker Configuration

## Specifications from middle_earth Models

### Dictionary
- **Type:** DICT_4X4_50
- **Description:** 4x4 bit ArUco dictionary with 50 unique markers

### Physical Dimensions
- **Plate size:** 0.1524 x 0.1524 meters (6" x 6")
- **Marker size (black square):** 0.12192 m — the texture has a 10% white margin on each side.
  This is the value to use as `marker_length`.
- **Thickness:** 0.001m (simulation model)

### Marker IDs
- **Range:** 0-19 (20 markers total)
- **Available IDs:** 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19

### Source Location
- **Model Path:** `src/middle_earth/models/aruco_marker/`
- **Textures:** `src/middle_earth/models/aruco_marker/materials/textures/`
- **SDF File:** `model.sdf`

## OpenCV Configuration

```cpp
// OpenCV ArUco Dictionary
cv::aruco::DICT_4X4_50

// Marker size in meters
const double MARKER_SIZE = 0.12192;  // black square, not the 0.1524 m plate

// Valid marker IDs
const std::vector<int> VALID_IDS = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
                                     10, 11, 12, 13, 14, 15, 16, 17, 18, 19};
```

## Usage Notes
- These markers are used in the middle_earth simulation environment
- Markers are static objects in the simulation
- Physical size is approximately 6 inches, suitable for close-range detection
- 4x4 dictionary provides good balance between detection speed and robustness
