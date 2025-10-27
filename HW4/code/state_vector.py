from tools.sim_tools import SimConnector
from tools.credentials import robot_id, password
import time

# connect to simulator
sim = SimConnector(robot_id, password)
sim.reset()

# get and print information
state = sim.get_drone_state()
print("Drone state:")
print(state)
