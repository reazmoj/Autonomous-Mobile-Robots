# In the name of God

import struct
import redis
import numpy as np
import cv2
from scipy.spatial.transform import Rotation as Rot


class SimConnector:
    def __init__(self, username, password, is_local=False):
        if is_local:
            r_ = redis.Redis(
                host="10.10.11.14", port=6379,
                username=username,
                password=password,
                ssl=False
            )
        else:
            r_ = redis.Redis(
                host="www2.aipark.ir", port=16824,
                username=username,
                password=password,
                ssl=False
            )
        self.id = username[1:]
        self.r = r_
        self.tic_time = -1.0
        self.__version__ = 1.2

    def reset(self):
        payload = struct.pack('<H', 0)
        self.r.publish("Hg6T%s-C" % self.id, payload)

    def send_motor_command(self, front_right, rear_left, front_left, rear_right, duration):
        payload = struct.pack('<Hfffff', 5, front_right, rear_left, front_left, rear_right, duration)
        self.r.publish("Hg6T%s-C" % self.id, payload)

    def get_cam_image(self, as_rgb=True):
        payload = self.r.get("Hg6T%s-cam" % self.id)
        jpg_as_np = np.frombuffer(payload, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        if as_rgb:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def get_drone_state(self):
        payload = self.r.get("Hg6T%s-S" % self.id)
        (ts, pox, poy, poz, orx, ory, orz, orw, lvx, lvy, lvz, avx, avy, avz, lax, lay, laz, hc, ls) = struct.unpack(
            "Qffffffffffffffffhh", payload)
        state = {'ts': ts, 'position': [pox, poy, poz], 'orientation': Rot.from_quat([orx, ory, orz, orw]),
                 'linear_velocity': [lvx, lvy, lvz], 'angular_velocity': [avx, avy, avz],
                 'linear_acceleration': [lax, lay, laz]}
        return state
