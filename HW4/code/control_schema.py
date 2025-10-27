########################################### Part 1 #########################################

import numpy as np
import time
from tools.sim_tools import SimConnector
from tools.credentials import robot_id, password
from tools.viewer import LiveViewer
import matplotlib.pyplot as plt

# connect to simulator
sim = SimConnector(robot_id, password)
sim.reset()
viewer = LiveViewer(sim, 3) 
viewer.start_view()

# control parameters
target_height = 20.0  # target height (m)
control_rate = 20.0  # (Htz)
control_period = 1.0 / control_rate  # (s)

# Primary PID values
kP, kD, kI = 1.0, 0.5, 0.1 
integral_error = 0.0
previous_error = 0.0


data_log = []

start_time = time.time()
while True:
    
    current_time = time.time() - start_time
    
    state = sim.get_drone_state()
    height = -state['position'][2]  
    vertical_velocity = -state['linear_velocity'][2]  
    
    # calculate errors
    position_error = target_height - height
    velocity_error = 0.0 - vertical_velocity
    integral_error += position_error * control_period
    derivative_error = (position_error - previous_error) / control_period

    # PID controler
    motor_command = kP * position_error + kD * velocity_error + kI * integral_error
    motor_command = max(0.35, min(1.0, motor_command))  

    sim.send_motor_command(motor_command, motor_command, motor_command, motor_command, control_period)

    data_log.append([current_time, height, motor_command])
    previous_error = position_error

    # loop timestamp
    time.sleep(control_period)

    if abs(position_error) < 0.1:  # break condition (error less than 10 cm)
        print("Target height reached!")
        break

# ploting 
data_log = np.array(data_log)
plt.figure(figsize=(10, 5))
plt.plot(data_log[:, 0], data_log[:, 1], label="Height (m)")
plt.plot(data_log[:, 0], data_log[:, 2], label="Motor Command")
plt.axhline(y=target_height, color='r', linestyle='--', label="Target Height")
plt.xlabel("Time (s)")
plt.ylabel("Values")
plt.title("Height Control (PID)")
plt.legend()
plt.grid()
plt.show()

############################################ Part 2 #########################################
# import numpy as np
# from tools.sim_tools import SimConnector
# from tools.credentials import robot_id, password
# from tools.viewer import LiveViewer
# import time

# sim = SimConnector(robot_id, password)
# sim.reset()
# viewer = LiveViewer(sim, 3) 
# viewer.start_view()

# k_p = 0.6
# k_i = 0.1
# k_d = 0.3
# integral_error = 0.0
# prev_error = 0.0
# control_rate = 20.0
# control_period = 1.0 / control_rate

# data_log = []
# start_time = time.time()

# while True:
#     t = time.time() - start_time
#     target_height = 15 + 5 * np.sin(0.4 * np.pi * t)

#     state = sim.get_drone_state()
#     current_height = -state['position'][2]
#     vertical_velocity = -state['linear_velocity'][2]

#     position_error = target_height - current_height
#     integral_error += position_error * control_period
#     derivative_error = (position_error - prev_error) / control_period
#     prev_error = position_error

#     motor_command = k_p * position_error + k_i * integral_error + k_d * derivative_error
#     motor_command = np.clip(motor_command, 0, 1)

#     sim.send_motor_command(motor_command, motor_command, motor_command, motor_command, control_period)
#     time.sleep(control_period)

#     data_log.append((t, current_height, target_height, motor_command))

#     if t > 20:  # loop terminate after 20 sec
#         break

# import matplotlib.pyplot as plt
# data_log = np.array(data_log)
# time_log = data_log[:, 0]
# height_log = data_log[:, 1]
# target_log = data_log[:, 2]
# command_log = data_log[:, 3]

# plt.figure()
# plt.subplot(3, 1, 1)
# plt.plot(time_log, target_log, label="Target Height")
# plt.plot(time_log, height_log, label="Actual Height")
# plt.xlabel("Time (s)")
# plt.ylabel("Height (m)")
# plt.legend()
# plt.title("Height vs Time")

# plt.subplot(3, 1, 2)
# plt.plot(time_log, command_log)
# plt.xlabel("Time (s)")
# plt.ylabel("Motor Command")
# plt.title("Motor Command vs Time")

# plt.tight_layout()
# plt.show()
