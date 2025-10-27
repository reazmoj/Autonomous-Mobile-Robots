# In the name of God


from tools.sim_tools import SimConnector
from tools.viewer import LiveViewer
from tools.gather_state import StateGatherer
import time
from tools.credentials import robot_id, password

sim = SimConnector(robot_id, password)
viewer = LiveViewer(sim, 5)
viewer.start_view()

state_collector = StateGatherer(sim)

sim.reset()
state_collector.start_gathering(15)
# Moving up slowly for 7.0 seconds
throttle = 0.7
sim.send_motor_command(throttle, throttle, throttle, throttle, 7.0)
time.sleep(7.0)

# Moving down for 3.0 seconds
throttle = 0.35
sim.send_motor_command(throttle, throttle, throttle, throttle, 3.0)
time.sleep(3.0)

# Moving up fast for 3.0 seconds
throttle = 1.0
sim.send_motor_command(throttle, throttle, throttle, throttle, 3.0)
time.sleep(3.0)

state_collector.stop_gathering()
state_collector.plot_height()
