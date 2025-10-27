# In the name of God

import time


class RateController:
    def __init__(self, rate):
        self.period = 1.0 / rate
        self.tic_time = time.time()

    def tic(self):
        self.tic_time = time.time()

    def wait(self):
        wa = self.get_wait_amount()
        if wa > 0:
            time.sleep(wa)

    def get_wait_amount(self):
        now = time.time()
        wait_duration = self.period - (now - self.tic_time)
        return max(wait_duration, 0)

