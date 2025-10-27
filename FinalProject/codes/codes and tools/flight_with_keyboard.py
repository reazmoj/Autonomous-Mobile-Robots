# In the name of God

from tools.sim_tools import SimConnector
from tools.simple_flight import SimpleFlight
from tools.credentials import robot_id, password
import cv2
import time

sim = SimConnector(robot_id, password, is_local=False)
SimpleFlight(sim)

# sim.teleport_to_position(-87.038,     -92.014,     -21.054,0,0,270)
sim.move_to_position(-224.58949279785156,
            -105.0,
            -14.227203369140625, 5, 10)
drone_state = sim.get_drone_state()

time.sleep(.5)
rgb_img, depth_img, depth_float, *_ = sim.get_joint_image()
dron_ori = drone_state["orientation"].as_quat()
print("Dron Pos: ", drone_state["position"])
print("Dron ori: ", dron_ori )
print('sequence of orientation: ', drone_state["orientation"])
# cv2.imwrite("D:/Lectures/Robot/final/FinalProject-v2/codes and tools/notebooks/rgb_img2.png", rgb_img)
# cv2.imwrite("D:/Lectures/Robot/final/FinalProject-v2/codes and tools/notebooks/depth_img2.png", depth_float)

# print(drone_state)


# sim.teleport_to_position(-500,-180,-20,0,0,0)


print('Hi - I am %s' % robot_id)
print('You can fly me with the following key combinations:')
print('Arrow keys: Up: Move forward, Down: Backward')
print('Arrow keys: Right: Rotate CW, Left: CCW')
print('PgUp: Move upward, PgDown: Downward')
print('Home: Go home, End: Immediate stop')
print('Space: Save snapshot, Esc: Quit')
print('You can also control me with other key combination or other logics')
print('For example you may want to control me not in the body frame but,')
print('in the world frame. This can be done using other provided flight')
print('functions in SimConnector class.')
