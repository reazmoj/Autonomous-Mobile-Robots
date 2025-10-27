# In the name of God

import time
from tools.sim_tools import SimConnector
from tools.viewer import LiveViewer
from tools.credentials import robot_id, password
import utils

# from ultralytics import YOLO
import numpy as np
import cv2
import json
import pandas as pd


calibration_data = utils.load_calibration_data("D:/Lectures/Robot/final/FinalProject-code/cam_calib/camera_calibration.npz")
detected_objects = []

def get_sim_data():
    rgb_img, depth_img, depth_float, *_ = sim.get_joint_image()
    drone_state = sim.get_drone_state()
    
    imgs_data = [rgb_img, depth_float]
    
    return imgs_data, drone_state

def detect_and_cordinate(counter):
    
    imgs_data, drone_state = get_sim_data()

    undistorted_img = utils.undistorted_imgs(imgs_data[0], calibration_data)
    
    detections = utils.detect_objects(undistorted_img)

    cam_rot, cam_pos = utils.get_camera_extrinsic(drone_state)

    if len(detections) > 0:
        cv2.imwrite(f'D:/Lectures/Robot/final/FinalProject-code/codes and tools/final/{counter}_rgb.png', imgs_data[0])
        cv2.imwrite(f'D:/Lectures/Robot/final/FinalProject-code/codes and tools/final/{counter}_depth.png', imgs_data[1])
        try:
            for det in detections:
                pos = utils.pixel_to_global(det['bbox'], imgs_data[1], cam_rot, cam_pos, calibration_data)
                cls = det['class']
                filter = utils.filter_detection(pos, cls, detected_objects)
                if not filter:
                    detected_objects.append({
                        'img_id': counter,
                        'class': det['class'], 
                        'position': pos.tolist(), 
                        'cam_pos': cam_pos.tolist(),
                        'drone_pos': drone_state['position'],
                        'dron_ori': drone_state['orientation'].as_quat().tolist(),
                        'bbox': det['bbox']
                    })

        except ValueError as error:
            print("Value error!!! ", error)
    # print(detected_objects)
    with open("sample.json", "w") as outfile:
        json.dump(detected_objects, outfile)

def get_depth(all_pixels=False):
    time.sleep(epsilon)
    depth_image = sim.get_joint_image()[2]

    if not all_pixels:
        depth_image = depth_image[:220, 241:542]

    return np.min(depth_image)

def get_h():
    time.sleep(0.1)
    return sim.get_drone_state()["position"][2]

def save_image(counter):
    # print(f"saving image ... {counter}")
    # sim.immediate_stop()
    time.sleep(epsilon)
    imgs = sim.get_joint_image()
    drone_state = sim.get_drone_state()

    x,y,z = drone_state["position"]
    ox,oy,oz = drone_state["orientation"].as_euler('zyx', 
                                              degrees=True)

    cv2.imwrite(f'D:/Lectures/Robot/final/FinalProject-v2/codes and tools/final/{counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_rgb.png', 
                imgs[0])
    cv2.imwrite(f'D:/Lectures/Robot/final/FinalProject-v2/codes and tools/final/{counter}_{x:.2f}_{y:.2f}_{z:.2f}_{ox:.2f}_{oy:.2f}_{oz:.2f}_depth.png', 
                imgs[2])

    return None

def adjust_altitude():
    while (depth := get_depth()) <= 14:
        # print(f"Depth: {depth}/nObject near .... Going Up 2 meters")
        sim.immediate_stop()
        time.sleep(0.1)
        sim.move_by_body_vels(0, 0, -2, 1)
        time.sleep(1.1)

    while (depth := get_depth(all_pixels=True)) >= 22:
        # print(f"Depth: {depth}/nObject far .... Going Down 2 meters")
        sim.immediate_stop()
        time.sleep(0.1)
        sim.move_by_body_vels(0, 0, 2, 1)
        time.sleep(1.1)



sim = SimConnector(robot_id, password, is_local=False)
viewer = LiveViewer(sim, 5, show_osd=True)
viewer.start_view(with_depth=False)

epsilon = 0.1  # seconds

sim.reset()

counter = 0

x = [-395, 195]
y = [-100, 110]
z = -10
movement = []

sim.teleport_to_position(x[0],y[0],z,0,0,0)
drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)

time.sleep(.1)
next_position = x[1],y[0], z

while viewer.is_live:
    if not viewer.is_live:
        break

    duration = 3
    sim.move_to_position(next_position[0], 
                         next_position[1], 
                         next_position[2],
                         4,
                         duration)

    time.sleep(duration+4)

    # detect_and_cordinate(counter)

    counter += 1

    drone_state = sim.get_drone_state()["position"]
    movement.append(drone_state)

    if drone_state[0]+5 >= x[1]:
        sim.immediate_stop()
        time.sleep(0.1)
        sim.rotate_to_yaw(90,3,0)
        time.sleep(3.5)
        sim.move_by_body_vels(10, 0, 0, 6)
        time.sleep(6.5)
        sim.rotate_to_yaw(180,3,0)
        time.sleep(3.1)
        now_position = sim.get_drone_state()["position"]
        next_position=x[0],now_position[1],z
        time.sleep(.1)

    if drone_state[0]-5 <= x[0]:
        sim.immediate_stop()
        time.sleep(0.1)
        sim.rotate_to_yaw(90,3,0)
        time.sleep(3.5)
        sim.move_by_body_vels(10, 0, 0, 6) 
        time.sleep(6.5)
        sim.rotate_to_yaw(0,3,0)
        time.sleep(3.1)
        now_position = sim.get_drone_state()["position"]
        next_position=x[1],now_position[1],z
        time.sleep(.1)
        time.sleep(3.1)
    # print(drone_state,next_position)         
    time.sleep(.1)


    adjust_altitude()

    if next_position[0] > x[1] and next_position[1] > y[1]:
        break


drone_state = sim.get_drone_state()["position"]
movement.append(drone_state)
print(len(movement))
# print(movement)
print("-" * 10)
DF = pd.DataFrame(movement) 
DF.to_csv("movement.csv")


