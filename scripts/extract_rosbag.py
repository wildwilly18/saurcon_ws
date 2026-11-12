#!/usr/bin/env python3

from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import rosbag2_py
import array
import csv
import json
from pathlib import Path
import numpy as np
from cv_bridge import CvBridge
import cv2

def extract_rosbag_to_csv_and_images(bag_path, output_dir):
    """
    Extract rosbag topics to CSV files and save images.
    
    Args:
        bag_path: Path to the rosbag directory
        output_dir: Output directory for CSV files and images
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for images
    image_dir = output_path / "camera_images"
    depth_dir = output_path / "depth_images"
    image_dir.mkdir(exist_ok=True)
    depth_dir.mkdir(exist_ok=True)
    
    # Initialize storage and reader
    storage_options = rosbag2_py.StorageOptions(uri=str(bag_path), storage_id='mcap')
    converter_options = rosbag2_py.ConverterOptions('', '')
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    
    # Get topic types
    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}
    
    # Dictionary to store CSV writers and files
    csv_files = {}
    csv_writers = {}
    
    # CvBridge for image conversion
    bridge = CvBridge()
    
    # Image counters
    image_count = 0
    depth_count = 0
    
    print(f"Starting extraction from {bag_path}")
    print(f"Output directory: {output_dir}")
    print(f"Topics found: {len(type_map)}")
    
    # Read messages
    while reader.has_next():
        (topic, data, timestamp) = reader.read_next()
        
        # Skip image topics for CSV (handle separately)
        if 'Image' in type_map[topic]:
            msg_type = get_message(type_map[topic])
            msg = deserialize_message(data, msg_type)
            
            # Convert ROS time to seconds
            time_sec = timestamp / 1e9
            
            if topic == '/camera/image':
                # Convert and save RGB image
                try:
                    cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                    filename = image_dir / f"frame_{image_count:06d}_{time_sec:.6f}.png"
                    cv2.imwrite(str(filename), cv_image)
                    image_count += 1
                    if image_count % 100 == 0:
                        print(f"Saved {image_count} camera images...")
                except Exception as e:
                    print(f"Error saving image {image_count}: {e}")
                    
            elif topic == '/camera/depth_image':
                # Convert and save depth image
                try:
                    cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                    filename = depth_dir / f"depth_{depth_count:06d}_{time_sec:.6f}.png"
                    # Normalize depth for visualization
                    cv_image_normalized = cv2.normalize(cv_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                    cv2.imwrite(str(filename), cv_image_normalized)
                    depth_count += 1
                    if depth_count % 100 == 0:
                        print(f"Saved {depth_count} depth images...")
                except Exception as e:
                    print(f"Error saving depth image {depth_count}: {e}")
            continue
        
        # Deserialize message
        msg_type = get_message(type_map[topic])
        msg = deserialize_message(data, msg_type)
        
        # Create CSV file for topic if not exists
        if topic not in csv_files:
            # Sanitize topic name for filename
            filename = topic.replace('/', '_').lstrip('_') + '.csv'
            filepath = output_path / filename
            csv_files[topic] = open(filepath, 'w', newline='')
            
            # Create CSV writer and write header
            csv_writers[topic] = csv.writer(csv_files[topic])
            
            # Generate header based on message type
            header = ['timestamp_ns', 'timestamp_sec']
            header.extend(get_message_fields(msg))
            csv_writers[topic].writerow(header)
            print(f"Created CSV for topic: {topic}")
        
        # Write data row
        row = [timestamp, timestamp / 1e9]  # Add timestamp in nanoseconds and seconds
        row.extend(extract_message_data(msg))
        csv_writers[topic].writerow(row)
    
    # Close all CSV files
    for f in csv_files.values():
        f.close()
    
    print(f"\nExtraction complete!")
    print(f"Total camera images saved: {image_count}")
    print(f"Total depth images saved: {depth_count}")
    print(f"CSV files saved to: {output_path}")

# Types rclpy uses for array fields (primitive arrays arrive as array.array or
# numpy arrays, arrays of messages as lists).
SEQUENCE_TYPES = (list, tuple, np.ndarray, array.array)


def _is_message(value):
    return hasattr(value, 'get_fields_and_field_types')


def _is_fixed_array(field_type):
    """True for fixed-size arrays such as 'double[36]' (not 'sequence<...>')."""
    return field_type.endswith(']') and not field_type.startswith('sequence')


def _to_plain(value):
    """Convert a field value to plain Python types that json can serialise."""
    if _is_message(value):
        return {name: _to_plain(getattr(value, name))
                for name in value.get_fields_and_field_types()}
    if isinstance(value, (bytes, bytearray)):
        return list(value)
    if isinstance(value, SEQUENCE_TYPES):
        return [_to_plain(v) for v in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def get_message_fields(msg, prefix=''):
    """Recursively get column names from a message.

    Fixed-size arrays get one column per element. Variable-length arrays get a
    single column holding a JSON list, so every row of a topic has the same
    number of columns regardless of how many elements each message carries.
    """
    fields = []

    for field, field_type in msg.get_fields_and_field_types().items():
        field_name = f"{prefix}{field}"
        field_value = getattr(msg, field)

        if _is_message(field_value):
            fields.extend(get_message_fields(field_value, f"{field_name}."))
        elif isinstance(field_value, SEQUENCE_TYPES) and _is_fixed_array(field_type) \
                and not any(_is_message(v) for v in field_value):
            fields.extend(f"{field_name}[{i}]" for i in range(len(field_value)))
        else:
            fields.append(field_name)

    return fields


def extract_message_data(msg):
    """Recursively extract data from a message (same column layout as get_message_fields)."""
    data = []

    for field, field_type in msg.get_fields_and_field_types().items():
        field_value = getattr(msg, field)

        if _is_message(field_value):
            data.extend(extract_message_data(field_value))
        elif isinstance(field_value, (bytes, bytearray)):
            data.append(json.dumps(list(field_value)))
        elif isinstance(field_value, SEQUENCE_TYPES):
            if _is_fixed_array(field_type) and not any(_is_message(v) for v in field_value):
                data.extend(_to_plain(field_value))
            else:
                data.append(json.dumps(_to_plain(field_value)))
        else:
            data.append(field_value)

    return data


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 extract_rosbag.py <bag_path> [output_dir]")
        print("Example: python3 extract_rosbag.py bags/rosbag_20251201_202722")
        sys.exit(1)
    
    bag_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else bag_path
    
    extract_rosbag_to_csv_and_images(bag_path, output_dir)
