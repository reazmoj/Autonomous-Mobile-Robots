# In the name of God

import datetime
import cv2
from tools.rate_controller import  RateController
from threading import Thread


class LiveViewer:
    def __init__(self, sim_connector, fps, show_osd=True):
        self.sim = sim_connector
        self.ratec = RateController(fps)
        self.viewer_th = Thread(target=self.viewer_worker)
        self.is_live = False
        self.show_osd = show_osd
        # cv2.namedWindow(self.sim.id, cv2.WINDOW_NORMAL)

    def add_osd(self, cv_image):
        fontFace = cv2.FONT_HERSHEY_PLAIN
        fontScale = 1.0
        thickness = 2
        state = self.sim.get_drone_state()
        dt = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=state['ts'] / 1000.0)
        t = dt.time()

        (roll, pitch, yaw) = state['orientation'].as_euler("XYZ", degrees=True)

        line1 = str.format("%02d:%02d:%02d.%03d" % (t.hour, t.minute, t.second, t.microsecond / 1000))
        cv2.putText(cv_image, line1, (10, 16), fontFace, fontScale, (255, 150, 150), thickness)
        line2 = str.format("x: %4.2f, y: %4.2f, z: %4.2f" % (state['position'][0], state['position'][1], state['position'][2]))
        cv2.putText(cv_image, line2, (10, 34), fontFace, fontScale, (200, 100, 200), thickness)
        line3 = str.format("roll: %4.2f, pitch: %4.2f, yaw: %4.2f" % (roll, pitch, yaw))
        cv2.putText(cv_image, line3, (10, 52), fontFace, fontScale, (100, 200, 100), thickness)
        return cv_image

    def viewer_worker(self):
        while self.is_live:
            self.ratec.tic()
            cv_img = self.sim.get_cam_image(False)
            if self.show_osd:
                cv_img = self.add_osd(cv_img)
            cv2.imshow(self.sim.id, cv_img)
            wait_amount = max(int(self.ratec.get_wait_amount()*1000.0), 1)
            key = cv2.waitKey(wait_amount)
            if key == 27:
                self.is_live = False

    def stop_view(self):
        self.is_live = False

    def start_view(self):
        self.is_live = True
        self.viewer_th.start()
