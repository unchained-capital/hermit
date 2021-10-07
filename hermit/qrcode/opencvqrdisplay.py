from .base import QRDisplay
import numpy as np
import cv2
from .utils import window_is_open

class OpenCVQRDisplay(QRDisplay):
    def __init__(self, qr_config):
        self.x_position = int(qr_config.get('x_position', 100))
        self.y_position = int(qr_config.get('y_position', 100))

    def animate_qrs(self, qrs: list) -> None:
        # Build images to display before we show the window.
        images = [qr.make_image(fill_color="black", back_color="white") for qr in qrs]
        images = [np.array(image.convert("RGB"))[:,:,::-1] for image in images]
        winname="displayqr"

        cv2.namedWindow(winname, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)
        cv2.resizeWindow(winname, 300, 300)
        cv2.setWindowProperty(winname, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
        cv2.moveWindow(winname, self.x_position, self.y_position)

        finished = False
        total = len(images)
        try:
            while not finished:
                for index, image in enumerate(images):
                    cv2.imshow(winname, image)
                    cv2.setWindowTitle(winname, f"QR Code {index+1} of {total}")

                    # Allow the window to update and wait for 200ms for a keypress
                    # if not True:
                    cv2.waitKey(1)
                    if not window_is_open(winname,200):
                        finished = True
                        break

        finally:
            cv2.destroyWindow(winname)
            cv2.waitKey(1)


    def setup_camera_display(self):
        # Dont include a toolbar or a status bar at the bottom.
        cv2.namedWindow("readqr", cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)

        # Move the window to a sane place on the screen
        cv2.moveWindow("readqr", self.x_position, self.y_position)

    def teardown_camera_display(self):
        cv2.destroyWindow("readqr")
        cv2.waitKey(1)

    def display_camera_image(self, image):
        cvimg = np.array(image)
        # RGB to BGR
        cvimg = cvimg[:, :, ::-1].copy()
        cv2.imshow("readqr", cvimg)
        return window_is_open("readqr", 100)
