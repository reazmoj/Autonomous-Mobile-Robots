# In the name of God

import datetime
import cv2
from tools.rate_controller import  RateController
from threading import Thread
from scipy.spatial.transform import Rotation as Rot
from ultralytics import YOLO
import utils
import json

calibration_data = utils.load_calibration_data("D:/Lectures/Robot/final/FinalProject-code/cam_calib/camera_calibration.npz")

__version__ = 1.13
model = YOLO("D:/Lectures/Robot/final/FinalProject-code/codes and tools/models/yolo11n.pt")

detected_objects = []

class LiveViewer:
    def __init__(self, sim_connector, fps, show_osd=True, key_call_back=None):
        self.sim = sim_connector
        self.ratec = RateController(fps)
        self.viewer_th = Thread(target=self.viewer_worker)
        self.is_live = False
        self.show_osd = show_osd
        self.key_call_back = key_call_back
        # cv2.namedWindow(self.sim.id, cv2.WINDOW_NORMAL)
        self.fldr = ''
        self.last_image = None
        self.img_cntr = 0
        self.with_depth = False
        self.init_folders()

    def init_folders(self):
        import os
        dt_str = datetime.datetime.now().strftime("%m-%d-%H-%M-%S")
        self.fldr = fldr = 'snapshots/%s/' % dt_str
        os.makedirs(self.fldr, exist_ok=True)

    def add_osd(self, cv_image):
        fontFace = cv2.FONT_HERSHEY_PLAIN
        fontScale = 1.0
        thickness = 2
        state = self.sim.get_drone_state()
        has_collided = state['has_collided']
        dt = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=state['ts'] / 1000.0)
        t = dt.time()

        (roll, pitch, yaw) = state['orientation'].as_euler("XYZ", degrees=True)

        line1 = str.format("%02d:%02d:%02d.%03d" % (t.hour, t.minute, t.second, t.microsecond / 1000))
        cv2.putText(cv_image, line1, (10, 16), fontFace, fontScale, (255, 150, 150), thickness)
        line2 = str.format("x: %4.2f, y: %4.2f, z: %4.2f" % (state['position'][0], state['position'][1], state['position'][2]))
        cv2.putText(cv_image, line2, (10, 34), fontFace, fontScale, (200, 100, 200), thickness)
        line3 = str.format("roll: %4.2f, pitch: %4.2f, yaw: %4.2f" % (roll, pitch, yaw))
        cv2.putText(cv_image, line3, (10, 52), fontFace, fontScale, (100, 200, 100), thickness)
        if has_collided == 1:
            line1_ = str.format("collided")
            cv2.putText(cv_image, line1_, (130, 16), fontFace, fontScale, (10, 10, 255), thickness)
        return cv_image

    def add_osd2(self, cv_image, ts, x, y, z, qx, qy, qz, qw):
        fontFace = cv2.FONT_HERSHEY_PLAIN
        fontScale = 1.0
        thickness = 2
        state = self.sim.get_drone_state()
        has_collided = state['has_collided']
        dt = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=ts / 1000.0)
        t = dt.time()

        (roll, pitch, yaw) = Rot.from_quat([qx, qy, qz, qw]).as_euler("XYZ", degrees=True)

        line1 = str.format("%02d:%02d:%02d.%03d" % (t.hour, t.minute, t.second, t.microsecond / 1000))
        cv2.putText(cv_image, line1, (10, 16), fontFace, fontScale, (255, 150, 150), thickness)
        line2 = str.format("x: %4.2f, y: %4.2f, z: %4.2f" % (x, y, z))
        cv2.putText(cv_image, line2, (10, 34), fontFace, fontScale, (200, 100, 200), thickness)
        line3 = str.format("roll: %4.2f, pitch: %4.2f, yaw: %4.2f" % (roll, pitch, yaw))
        cv2.putText(cv_image, line3, (10, 52), fontFace, fontScale, (100, 200, 100), thickness)
        if has_collided == 1:
            line1_ = str.format("collided")
            cv2.putText(cv_image, line1_, (130, 16), fontFace, fontScale, (10, 10, 255), thickness)
        return cv_image

    def save_images(self):
        self.img_cntr += 1
        fname = '%s%03d.jpg' % (self.fldr, self.img_cntr)
        cv2.imwrite(fname, self.last_image)
        print('saving snapshot into: %s' % fname)

    def save_images2(self,img):
        self.img_cntr += 1
        fname = '%s%03d.jpg' % (self.fldr, self.img_cntr)
        cv2.imwrite(fname, img)
        print('saving snapshot into: %s' % fname)

    def viewer_worker(self):
        while self.is_live:
            self.ratec.tic()

            if self.with_depth:
                cv_img, depth_img, depth_float, *_ = self.sim.get_joint_image()
                if self.show_osd:
                    cv_img = self.add_osd(cv_img)
                final_image = cv2.hconcat([cv_img, depth_img])
            else:
                cv_img, depth_img, depth_float,ts1, *_ = self.sim.get_joint_image()
                state = self.sim.get_drone_state()
                self.last_image = cv_img.copy()
                if self.show_osd:
                    cv_img = self.add_osd(cv_img)
                    # cv_img = self.add_osd2(cv_img, ts, x, y, z, qx, qy, qz, qw)
                final_image = cv_img


            cam_rot, cam_pos = utils.get_camera_extrinsic(state)

            results = model(final_image, classes=[0,1,2,3,4])
            detections = []
            for box in results[0].boxes:
                cls_id = int(box.cls)
                if model.names[cls_id] in ['motorcycle', 'bicycle'] and box.conf > .25: 
                    detections.append({
                        'bbox': box.xyxy[0].tolist(),
                        'class': model.names[cls_id]
                    })
   
            if len(detections) > 0:
                for det in detections:
                    pos = utils.pixel_to_global(det['bbox'], depth_float, cam_rot, cam_pos, calibration_data)
                    cls = det['class']
                    filter = utils.filter_detection(pos, cls, detected_objects)
                    if not filter:
                        detected_objects.append({
                            'class': det['class'], 
                            'position': pos.tolist(), 
                            'cam_pos': cam_pos.tolist(),
                            'drone_pos': state['position'],
                            'dron_ori': state['orientation'].as_quat().tolist(),
                            'bbox': det['bbox']
                        })
            with open("samples_2.json", "w") as outfile:
                json.dump(detected_objects, outfile)
            final_image = results[0].plot()
            


            cv2.imshow(self.sim.id, final_image)
            # self.save_images2(final_image)

            wait_amount = max(int(self.ratec.get_wait_amount()*1000.0), 1)
            key = cv2.waitKeyEx(wait_amount)
            if self.key_call_back:
                self.key_call_back(key)
            elif key == 27:
                self.is_live = False

    def stop_view(self):
        self.is_live = False

    def start_view(self, with_depth=False):
        self.is_live = True
        self.with_depth = with_depth
        self.viewer_th.start()
