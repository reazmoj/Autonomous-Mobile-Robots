# In the name of God

from tools.viewer import LiveViewer


class SimpleFlight:
    def __init__(self, sim_connector):
        self.sim = sim_connector
        self.viewer = LiveViewer(sim_connector, 5, show_osd=True, key_call_back=self.handle_key)
        self.viewer.start_view(with_depth=True)

    def handle_key(self, key):
        # print(key)
        if key == -1:
            pass
        elif key == 65362 or key == 2490368 or key == 56:  # up
            self.sim.move_by_body_vels(10, 0, 0, 1)
        elif key == 65364 or key == 2621440 or key == 50:  # down
            self.sim.move_by_body_vels(-10, 0, 0, 1)
        elif key == 65361 or key == 2424832 or key == 52:  # left
            self.sim.rotate_yaw_rate(-10.1, 1)
        elif key == 65363 or key == 2555904 or key == 54:  # right
            self.sim.rotate_yaw_rate(10.1, 1)
        elif key == 65365 or key == 2162688 or key == 57:  # pgup
            self.sim.move_by_body_vels(0, 0, -5, 1)
        elif key == 65366 or key == 2228224 or key == 51:  # pgdown
            self.sim.move_by_body_vels(0, 0, 5, 1)
        elif key == 65360 or key == 2359296 or key == 55:  # home
            self.sim.reset()
        elif key == 65367 or key == 2293760 or key == 55:  # end - stop
            self.sim.immediate_stop()
        elif key == 65379:  # cam pitch up
            self.sim.set_main_cam_pose(0, -5, 0)
        elif key == 65535:  # cam pitch down
            self.sim.set_main_cam_pose(0, -85, 0)
        elif key == 32:  # space - save image
            self.viewer.save_images()
        elif key == 27:
            self.viewer.is_live = False