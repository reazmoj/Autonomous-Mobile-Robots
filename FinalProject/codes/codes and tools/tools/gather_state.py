# In the name of God

import numpy as np
import matplotlib.pyplot as plt
from tools.rate_controller import  RateController
from threading import Thread

class StateGatherer:
    def __init__(self, sim_connector):
        self.sim = sim_connector
        self.ratec = None
        self.gathering_th = Thread(target=self.gatherer_worker)
        self.do_gather = False
        self.gathered_data = []

    def gatherer_worker(self):
        while self.do_gather:
            self.ratec.tic()
            state = self.sim.get_drone_state()
            ts = state['ts']
            (x, y, z) = state['position']
            (qx, qy, qz, qw) = state['orientation'].as_quat()
            (vx, vy, vz) = state['linear_velocity']
            (ax, ay, az) = state['linear_acceleration']
            (avx, avy, avz) = state['angular_velocity']
            # if state['has_collided'] == 1:
            #     print('it is collided')
            row = [ts, x, y, z, qx, qy, qz, vx, vy, vz, ax, ay, az, avx, avy, avz]
            self.gathered_data.append(row)
            self.ratec.wait()

    def start_gathering(self, rate):
        self.ratec = RateController(rate)
        self.gathered_data = []
        self.do_gather = True
        self.gathering_th.start()

    def stop_gathering(self):
        self.do_gather = False

    def plot_height(self):
        data = np.array(self.gathered_data)
        plt.plot((data[:, 0]-data[0, 0])/1e9, -data[:, 3], label='Height', color='blue')

        plt.title('Drone Height')
        plt.xlabel('Time (s)')
        plt.ylabel('Height (m)')
        plt.legend()
        plt.grid()
        plt.show(block=True)
