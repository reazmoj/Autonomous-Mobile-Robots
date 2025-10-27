# In the name of God

import struct
import redis
import numpy as np
import cv2
from scipy.spatial.transform import Rotation as Rot
import zlib

__version__ = 1.13


class SimConnector:
    def __init__(self, username, password, is_local=False):
        if is_local:
            r_ = redis.Redis(
                host="127.0.0.1", port=6379, #100.100.110.140
                # username=username,
                # password=password,
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
        self.c_key = "Hg6T%s-C" % self.id
        self.s_key = "Hg6T%s-S" % self.id
        self.cam1_key = "Hg6T%s-cam" % self.id
        self.cam2_key = "Hg6T%s-depth" % self.id
        self.jointcam_key = "Hg6T%s-camdepth" % self.id

    def hover(self):
        payload = struct.pack('<H', 1)
        self.r.publish(self.c_key, payload)

    def immediate_stop(self):
        payload = struct.pack('<H', 0)
        self.r.publish(self.c_key, payload)

    def reset(self):
        payload = struct.pack('<H', 2)
        self.r.publish(self.c_key, payload)

    def send_motor_command(self, front_right, rear_left, front_left, rear_right, duration):
        payload = struct.pack('<Hfffff', 5, front_right, rear_left, front_left, rear_right, duration)
        self.r.publish(self.c_key, payload)

    # yaw: NED(degrees), timeout: seconds, error_margin (degrees?)
    def rotate_to_yaw(self, yaw, timeout, error_margin):
        payload = struct.pack('<Hfff', 7, yaw, timeout, error_margin)
        self.r.publish(self.c_key, payload)

    # yaw_rate (degrees?/s), duration: seconds
    def rotate_yaw_rate(self, yaw_rate, duration):
        payload = struct.pack('<Hff', 6, yaw_rate, duration)
        self.r.publish(self.c_key, payload)

    # vx, vy, vz: Body (m/s), velocity (m/s?), duration: seconds
    def move_by_body_vels(self, vx, vy, vz, duration):
        payload = struct.pack('<Hffff', 3, vx, vy, vz, duration)
        self.r.publish(self.c_key, payload)

    # x, y, z: NED (meters), velocity (m/s?), timeout: seconds
    def move_to_position(self, x, y, z, velocity, timeout):
        payload = struct.pack('<Hfffff', 4, x, y, z, velocity, timeout)
        self.r.publish(self.c_key, payload)

    def teleport_to_position(self, x, y, z, roll, pitch, yaw):
        payload = struct.pack('<HffffffL', 8, x, y, z, roll, pitch, yaw, 3934018435)
        self.r.publish(self.c_key, payload)

    def set_main_cam_pose(self, roll, pitch, yaw):
        payload = struct.pack('<Hffffff', 31, -1, -1, -1, roll, pitch, yaw)
        self.r.publish(self.c_key, payload)

    def set_depth_cam_pose(self, roll, pitch, yaw):
        payload = struct.pack('<Hffffff', 32, -1, -1, -1, roll, pitch, yaw)
        self.r.publish(self.c_key, payload)

    def get_cam_image(self, as_rgb=True):
        payload = self.r.get(self.cam1_key)
        l = struct.unpack('<l', payload[:4])[0]
        (ts, x, y, z, qx, qy, qz, qw, byte_encode) = struct.unpack('<Qfffffff%ds' % l, payload[4:])
        jpg_as_np = np.frombuffer(byte_encode, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        if as_rgb:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img, ts, x, y, z, qx, qy, qz, qw

    def get_depth_image(self, as_rgb=True):
        payload = self.r.get(self.cam2_key)
        l = struct.unpack('<l', payload[:4])[0]
        (ts, x, y, z, qx, qy, qz, qw, byte_encode) = struct.unpack('<Qfffffff%ds' % l, payload[4:])
        jpg_as_np = np.frombuffer(byte_encode, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        if as_rgb:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img, ts, x, y, z, qx, qy, qz, qw

    @staticmethod
    def __decode_image_data__(data):
        l = struct.unpack('<l', data[:4])[0]
        (ts, x, y, z, qx, qy, qz, qw, byte_encode) = struct.unpack('<Qfffffff%ds' % l, data[4:])
        jpg_as_np = np.frombuffer(byte_encode, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        return img, ts, x, y, z, qx, qy, qz, qw

    @staticmethod
    def __decode_depth_image__(data):
        l, ts, x, y, z, qx, qy, qz, qw, rows, cols = struct.unpack('<lQfffffffHH', data[:44])
        decompressed_byte_data = zlib.decompress(data[44:])
        depth_img = np.frombuffer(decompressed_byte_data, dtype=np.uint16)
        depth_float = depth_img.reshape([rows, cols]).astype(np.float64)
        depth_float /= 8.0
        img2d = depth_float.copy()
        max_depth = 80.0
        img2d[img2d > max_depth] = max_depth
        img2d /= max_depth
        img2d = img2d * 255.0
        img2d = img2d.astype(np.uint8)
        img = cv2.cvtColor(img2d, cv2.COLOR_GRAY2BGR)
        return img, depth_float, ts, x, y, z, qx, qy, qz, qw

    def get_joint_image(self):
        payload = self.r.get(self.jointcam_key)
        l1 = struct.unpack('<l', payload[:4])[0]
        img1, ts1, x1, y1, z1, qx1, qy1, qz1, qw1 = SimConnector.__decode_image_data__(payload[:(l1+4+36)])
        img2, depth_float, ts2, x2, y2, z2, qx2, qy2, qz2, qw2 = SimConnector.__decode_depth_image__(payload[(l1+4+36):])
        return img1, img2, depth_float, ts1, ts2, x1, y1, z1, qx1, qy1, qz1, qw1, x2, y2, z2, qx2, qy2, qz2, qw2

    def get_drone_state(self):
        payload = self.r.get(self.s_key)
        (ts, pox, poy, poz, orx, ory, orz, orw, lvx, lvy, lvz, avx, avy, avz, lax, lay, laz, hc, ls) = struct.unpack(
            "<Qffffffffffffffffhh", payload)
        state = {'ts': ts, 'position': [pox, poy, poz], 'orientation': Rot.from_quat([orx, ory, orz, orw]),
                 'linear_velocity': [lvx, lvy, lvz], 'angular_velocity': [avx, avy, avz],
                 'linear_acceleration': [lax, lay, laz], 'has_collided': hc}
        return state
