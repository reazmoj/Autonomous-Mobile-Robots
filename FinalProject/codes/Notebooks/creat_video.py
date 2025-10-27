import cv2
import os
import json
from typing import List, Dict

# Step 1: Load the dictionary
file_path = 'D:/Lectures/Robot/final/FinalProject-v2/sample.json'
with open(file_path, 'r') as f:
        data = json.load(f)

# Step 2: Define paths
input_image_folder = "D:/Lectures/Robot/final/FinalProject-v2/codes and tools/final/images"  # Folder containing images named as img_<id>.jpg
output_image_folder = "D:/Lectures/Robot/final/FinalProject-v2/codes and tools/final/image_detected"  # Folder to save images with bounding boxes
output_video_path = "D:/Lectures/Robot/final/FinalProject-v2/codes and tools/final/output_video.mp4"  # Path to save the output video

# Create output folder if it doesn't exist
os.makedirs(output_image_folder, exist_ok=True)

# Step 3: Process each entry in the data
image_paths = []
for entry in data:
    img_id = entry["img_id"]
    bbox = entry["bbox"]

    # Construct image file name
    image_filename = f"{img_id}_rgb.png"
    image_path = os.path.join(input_image_folder, image_filename)

    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"Image {image_path} not found. Skipping...")
        continue

    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Failed to load image {image_path}. Skipping...")
        continue

    # Draw the bounding box
    x_min, y_min, x_max, y_max = map(int, bbox)
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)  # Green color, thickness 2

    # Add class label
    label = entry["class"]
    cv2.putText(image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Save the modified image
    output_image_path = os.path.join(output_image_folder, image_filename)
    cv2.imwrite(output_image_path, image)
    image_paths.append(output_image_path)

# Step 4: Create a video from the images
if len(image_paths) > 0:
    # Get the dimensions of the first image
    first_image = cv2.imread(image_paths[0])
    height, width, layers = first_image.shape

    # Define the video codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, 1.0, (width, height))  # 1 frame per second

    # Write each image to the video
    for image_path in image_paths:
        frame = cv2.imread(image_path)
        video_writer.write(frame)

    # Release the video writer
    video_writer.release()

    print(f"Video saved to {output_video_path}")
else:
    print("No images processed. Video creation skipped.")