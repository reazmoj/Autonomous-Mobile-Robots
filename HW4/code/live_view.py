# In the name of God

from tools.sim_tools import SimConnector
from tools.viewer import LiveViewer
from tools.credentials import robot_id, password

sim = SimConnector(robot_id, password)
viewer = LiveViewer(sim, 5)
viewer.start_view()
