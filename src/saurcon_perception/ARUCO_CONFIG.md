# ArUco Marker Configuration

## Specifications from middle_earth Models

### Dictionary
- **Type:** DICT_4X4_50
- **Description:** 4x4 bit ArUco dictionary with 50 unique markers

### Physical Dimensions
- **Size:** 0.1524 x 0.1524 meters
- **Size (inches):** 6" x 6"
- **Size (mm):** 152.4mm x 152.4mm
- **Thickness:** 0.001m (simulation model)

### Marker IDs
- **Range:** 0-19 (20 markers total)
- **Available IDs:** 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19

### Source Location
- **Model Path:** `/home/wilson/saurcon_ws/src/middle_earth/models/aruco_marker/`
- **Textures:** `/home/wilson/saurcon_ws/src/middle_earth/models/aruco_marker/materials/textures/`
- **SDF File:** `model.sdf`

## OpenCV Configuration

```cpp
// OpenCV ArUco Dictionary
cv::aruco::DICT_4X4_50

// Marker size in meters
const double MARKER_SIZE = 0.1524;

// Valid marker IDs
const std::vector<int> VALID_IDS = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
                                     10, 11, 12, 13, 14, 15, 16, 17, 18, 19};
```

## Usage Notes
- These markers are used in the middle_earth simulation environment
- Markers are static objects in the simulation
- Physical size is approximately 6 inches, suitable for close-range detection
- 4x4 dictionary provides good balance between detection speed and robustness
