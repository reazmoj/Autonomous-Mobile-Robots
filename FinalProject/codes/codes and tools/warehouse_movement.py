import time
import numpy as np
import cv2
import pandas as pd
from tools.sim_tools import SimConnector
from tools.viewer import LiveViewer
from tools.credentials import robot_id, password

def get_depth(sim):
    time.sleep(epsilon)
    depth_image = sim.get_joint_image()[2][:220,240:540]
    depth_image = np.ravel(depth_image)
    return min(depth_image)

def get_h(sim):
    time.sleep(0.1)
    return sim.get_drone_state()["position"][2]

def move_forward(sim, duration, speed=2):
    sim.move_by_body_vels(speed, 0, 0, duration)
    time.sleep(duration + epsilon)

def rotate_yaw(sim, angle, duration=3):
    sim.rotate_yaw_rate(angle / duration, duration)
    time.sleep(duration + epsilon)

def zig_zag_movement(sim, movement, x_out):
    min_depth = 4.5
    direction = 1  # 1 for left-to-right, -1 for right-to-left

    while viewer.is_live:
        # Save current position and image
        drone_state = sim.get_drone_state()["position"]
        movement.append(drone_state)

        # Control altitude
        h = get_h(sim)
        if h < x[2] - 0.5:
            sim.move_by_body_vels(0, 0, 1, 0.5)
        elif h > x[2] + 0.5:
            sim.move_by_body_vels(0, 0, -1, 0.5)

        # Move forward
        move_forward(sim, 2)

        # Check depth and turn if necessary
        depth = get_depth(sim)
        if depth <= min_depth:
            if direction == 1:
                print("Turning right")
                rotate_yaw(sim, 90)
                move_forward(sim, 2)  # Move to the next row
                rotate_yaw(sim, 90)
                direction = -1
            else:
                print("Turning left")
                rotate_yaw(sim, -90)
                move_forward(sim, 2)  # Move to the next row
                rotate_yaw(sim, -90)
                direction = 1

        # Exit condition
        if drone_state[1] < x_out[1] + 6:
            sim.immediate_stop()
            sim.move_to_position(x_out[0], x_out[1], x_out[2], 2, 4)
            break

# Initialize simulation and viewer
sim = SimConnector(robot_id, password, is_local=False)
viewer = LiveViewer(sim, 5, show_osd=True)
viewer.start_view(with_depth=False)

sim.reset()
epsilon = 0.5

# Initial position
x = [-215, -20, -5.5]
x_out = [-215, -55, -5.5]
sim.teleport_to_position(x[0], x[1], x[2], 0, 0, 270)
time.sleep(epsilon)

movement = []
drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)

# Enter the warehouse and start zig-zag movement
rotate_yaw(sim, -90)  # Rotate towards the wall
zig_zag_movement(sim, movement, x_out)

# Save final position
drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)

# Save movement data to CSV
DF = pd.DataFrame(movement)
DF.to_csv("data_with_timestamp_2.csv", index=False)

print("Movement completed and data saved.")