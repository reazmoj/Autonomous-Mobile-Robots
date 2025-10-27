import json
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import List, Dict
import argparse

CLASS_MARKERS = {
    'car': 's',
    'person': 'o',
    'helicopter': 'D'
}

def parse_json_data(file_path: str) -> List[Dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found at: {file_path}")
    with open(file_path, 'r') as f:
        return json.load(f)

def create_2d_plot(data: List[Dict], output_path: str = 'drone_path.png') -> str:
    plt.figure(figsize=(12, 8))
    
    # Drone path
    drone_x = [d['drone_pos'][0] for d in data]
    drone_y = [d['drone_pos'][1] for d in data]
    plt.plot(drone_x, drone_y, 'b-', label='Drone Path', linewidth=2, alpha=0.7)
    
    # Camera positions
    cam_x = [d['cam_pos'][0] for d in data]
    cam_y = [d['cam_pos'][1] for d in data]
    plt.scatter(cam_x, cam_y, c='red', marker='^', s=80, 
                label='Camera Positions', edgecolor='black')
    
    # Object positions
    handled_classes = set()
    for d in data:
        marker = CLASS_MARKERS.get(d['class'], 'x')
        if d['class'] not in handled_classes:
            plt.scatter(d['position'][0], d['position'][1], 
                        marker=marker, s=60, label=d['class'].title())
            handled_classes.add(d['class'])
        else:
            plt.scatter(d['position'][0], d['position'][1], 
                        marker=marker, s=60)

    plt.xlabel('X Coordinate (m)')
    plt.ylabel('Y Coordinate (m)')
    plt.title('Drone Flight Visualization')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(output_path, dpi=300)
    plt.close()
    return output_path

def plot_elevation_profile(data: List[Dict], output_path: str = 'elevation_profile.png') -> str:
    positions = np.array([d['drone_pos'] for d in data])
    distances = np.cumsum(np.sqrt(np.sum(np.diff(positions[:, :2], axis=0)**2, axis=1)))
    distances = np.insert(distances, 0, 0)
    
    plt.figure(figsize=(12, 5))
    plt.plot(distances, positions[:, 2], 'b-', linewidth=2)
    plt.fill_between(distances, positions[:, 2], color='blue', alpha=0.1)
    
    plt.title('Drone Elevation Profile')
    plt.xlabel('Cumulative Distance (m)')
    plt.ylabel('Altitude (m)')
    plt.grid(True, alpha=0.3)
    plt.savefig(output_path, dpi=300)
    plt.close()
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize drone data')
    parser.add_argument('json_path', help='Path to JSON file')
    parser.add_argument('--plot-output', default='drone_plot.png', help='Main visualization output')
    parser.add_argument('--elevation-output', default='elevation.png', help='Elevation profile output')
    args = parser.parse_args()
    
    data = parse_json_data(args.json_path)
    create_2d_plot(data, args.plot_output)
    plot_elevation_profile(data, args.elevation_output)