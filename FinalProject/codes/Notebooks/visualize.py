import json
import folium
from typing import List, Dict
import argparse
import os

# Define a dictionary for mapping classes to icons
ICON_MAP = {
    "person": "user",
    "car": "car",
    "helicopter": "helicopter",
    "airplane": "plane",
    "camera": "camera"
}

def parse_json_data(file_path: str) -> List[Dict]:
    """Parse the custom JSON file with object positions."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found at: {file_path}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    parsed_data = []
    for item in data:
        # Extract relevant information
        position = item.get("position", [])
        cam_pos = item.get("cam_pos", [])
        
        if len(position) != 3 or len(cam_pos) != 3:
            raise ValueError("Position and cam_pos must have 3 values (x, y, z)")
        
        parsed_data.append({
            "class": item["class"],
            "position": position,
            "cam_pos": cam_pos
        })
    return parsed_data

def create_interactive_map(data: List[Dict], output_path: str = 'object_positions.html') -> str:
    """Create an interactive map with object positions and icons."""
    # Use the first camera position as the starting point for the map
    start_coord = tuple(data[0]["cam_pos"][:2])  # Assuming the first two elements are lat/lon
    
    m = folium.Map(
        location=start_coord,
        zoom_start=15,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Satellite'
    )
    
    # Add markers for each object
    camera_positions = []  # To store camera positions for connecting lines
    for obj in data:
        position = tuple(obj["position"][:2])  # Assuming the first two elements are lat/lon
        obj_class = obj["class"]
        
        # Add object marker with position details in the popup
        if obj_class in ICON_MAP:
            icon = folium.Icon(icon=ICON_MAP[obj_class], prefix="fa")
        else:
            icon = folium.Icon(color="blue")  # Default icon for unknown classes
        
        folium.Marker(
            location=position,
            popup=f"{obj_class.capitalize()}<br>Position: {obj['position']}",
            icon=icon
        ).add_to(m)
        
        # Add camera position marker
        cam_position = tuple(obj["cam_pos"][:2])
        camera_positions.append(cam_position)
        folium.Marker(
            location=cam_position,
            popup=f"Camera Position<br>{obj['cam_pos']}",
            icon=folium.Icon(color="green", icon="camera", prefix="fa")
        ).add_to(m)
    
    # Draw a line connecting camera positions sequentially
    if len(camera_positions) > 1:
        folium.PolyLine(
            camera_positions,
            color='purple',
            weight=2.5,
            opacity=0.8,
            tooltip='Camera Path'
        ).add_to(m)
    
    # Save the map
    m.save(output_path)
    return os.path.abspath(output_path)

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Visualize object positions from JSON file')
    parser.add_argument('json_path', help='Path to your JSON file')
    parser.add_argument('--output', help='Output path for the interactive map', default='object_positions.html')
    args = parser.parse_args()
    
    try:
        # Load and process coordinates
        data = parse_json_data(args.json_path)
        
        # Generate the interactive map
        map_path = create_interactive_map(data, args.output)
        
        print(f"Interactive map saved to: {map_path}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        exit(1)


# ===============================================================================

# import json
# import os
# from PIL import Image, ImageDraw
# import matplotlib.pyplot as plt

# def parse_json_data(file_path: str) -> List[Dict]:
#     """Parse the custom JSON file with object positions."""
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"JSON file not found at: {file_path}")
    
#     with open(file_path, 'r') as f:
#         data = json.load(f)
    
#     return data

# def draw_bounding_boxes_on_image(image_path: str, bboxes: List[List[float]], output_path: str):
#     """Draw bounding boxes on an image and save it."""
#     try:
#         img = Image.open(image_path)
#         draw = ImageDraw.Draw(img)
        
#         for bbox in bboxes:
#             # Assuming bbox format: [x_min, y_min, x_max, y_max]
#             draw.rectangle(bbox, outline="red", width=2)
        
#         img.save(output_path)
#     except Exception as e:
#         print(f"Error processing image {image_path}: {str(e)}")

# def process_images(json_data: List[Dict], image_dir: str, output_dir: str):
#     """Process images by drawing bounding boxes and saving them."""
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    
#     for obj in json_data:
#         img_id = obj["img_id"]
#         bbox = obj["bbox"]
#         image_name = f"img_{img_id}.jpg"  # Assuming image names are like "img_3.jpg"
#         input_image_path = os.path.join(image_dir, image_name)
#         output_image_path = os.path.join(output_dir, f"annotated_{image_name}")
        
#         if os.path.exists(input_image_path):
#             draw_bounding_boxes_on_image(input_image_path, [bbox], output_image_path)
#         else:
#             print(f"Image not found: {input_image_path}")

# if __name__ == "__main__":
#     # Set up paths
#     json_file = "path/to/your/json/file.json"
#     image_directory = "path/to/your/images"
#     output_directory = "path/to/save/annotated/images"
    
#     # Parse JSON data
#     data = parse_json_data(json_file)
    
#     # Process images
#     process_images(data, image_directory, output_directory)
    
#     print("Annotated images saved to:", output_directory)


# =========================================================================
# import json
# import os
# from PIL import Image, ImageDraw
# import plotly.express as px
# import base64
# from io import BytesIO

# def parse_json_data(file_path: str) -> List[Dict]:
#     """Parse the custom JSON file with object positions."""
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"JSON file not found at: {file_path}")
    
#     with open(file_path, 'r') as f:
#         data = json.load(f)
    
#     return data

# def draw_bounding_box_and_encode(image_path: str, bbox: List[float]) -> str:
#     """Draw bounding box on an image and encode it as base64."""
#     try:
#         img = Image.open(image_path)
#         draw = ImageDraw.Draw(img)
#         draw.rectangle(bbox, outline="red", width=2)
        
#         buffered = BytesIO()
#         img.save(buffered, format="PNG")
#         img_str = base64.b64encode(buffered.getvalue()).decode()
#         return f"data:image/png;base64,{img_str}"
#     except Exception as e:
#         print(f"Error processing image {image_path}: {str(e)}")
#         return ""

# def create_interactive_plot(json_data: List[Dict], image_dir: str):
#     """Create an interactive plot with hover/click functionality."""
#     data_points = []
#     for obj in json_data:
#         img_id = obj["img_id"]
#         position = obj["position"][:2]  # Use first two coordinates for plotting
#         bbox = obj["bbox"]
#         image_name = f"img_{img_id}.jpg"  # Assuming image names are like "img_3.jpg"
#         image_path = os.path.join(image_dir, image_name)
        
#         if os.path.exists(image_path):
#             encoded_image = draw_bounding_box_and_encode(image_path, bbox)
#             data_points.append({
#                 "x": position[0],
#                 "y": position[1],
#                 "class": obj["class"],
#                 "image": encoded_image
#             })
#         else:
#             print(f"Image not found: {image_path}")
    
#     # Create the plot
#     fig = px.scatter(
#         data_points,
#         x="x",
#         y="y",
#         title="Object Positions",
#         hover_name="class",
#         labels={"x": "X Position", "y": "Y Position"}
#     )
    
#     # Add hover data with images
#     for point in data_points:
#         fig.add_trace(
#             px.imshow(
#                 base64.b64decode(point["image"].split(",")[1]),
#                 binary_format="png"
#             ).data[0]
#         )
    
#     fig.update_traces(
#         customdata=[point["image"] for point in data_points],
#         hovertemplate="<b>%{hovertext}</b><br><extra></extra>"
#     )
    
#     fig.show()

# if __name__ == "__main__":
#     # Set up paths
#     json_file = "path/to/your/json/file.json"
#     image_directory = "path/to/your/images"
    
#     # Parse JSON data
#     data = parse_json_data(json_file)
    
#     # Create interactive plot
#     create_interactive_plot(data, image_directory)