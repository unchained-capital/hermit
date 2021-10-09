from typing import Optional

import numpy as np
import cv2
from qrcode import QRCode

from ..qr import qr_to_image
from .base import Display


def window_is_open(window_name: str, delay: Optional[int] = 1) -> bool:

    #
    # waitKey returns -1 if *no* keys were pressed during the delay.
    # If any key was pressed during the delay, it returns the code of
    # that key.
    #
    # As written, this variable is a boolean.
    #

    no_keys_pressed_during_delay = cv2.waitKey(delay) == -1

    #
    # On systems which support window properties (e.g. Qt backends
    # such as Linux) this is 0 or 1 (actually floats of those for some
    # damn reason).
    #
    # On a Mac, where window properties are not supported, this comes
    # out to -1.
    #

    window_is_visible_value = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
    window_is_visible = window_is_visible_value != 0

    #
    # We want both conditions
    #

    return no_keys_pressed_during_delay and window_is_visible


class OpenCVDisplay(Display):
    def __init__(self, io_config):
        Display.__init__(self, io_config)
        self.qr_window_name = "displayqr"
        self.camera_window_name = "readqr"

    #
    # Displaying QRs
    #

    def format_qr(self, qr: QRCode) -> bytes:
        return np.array(qr_to_image(qr).convert("RGB"))[:, :, ::-1]

    def animate_qrs(self, qrs: list) -> None:
        # Build images to display before we show the window.
        images = [self.format_qr(qr) for qr in qrs]

        self.create_window(self.qr_window_name, preserve_ratio=True)

        finished = False
        total = len(images)
        try:
            while not finished:
                for index, image in enumerate(images):
                    cv2.imshow(self.qr_window_name, image)
                    cv2.setWindowTitle(
                        self.qr_window_name, f"QR Code {index+1} of {total}"
                    )

                    # We need to wait at least 1 tick to give OpenCV time to
                    # process the directions above.
                    cv2.waitKey(1)

                    # Wait for a keypress...
                    if not window_is_open(
                        self.qr_window_name, self.qr_code_sequence_delay_ms
                    ):
                        finished = True
                        break

        finally:
            self.destroy_window(self.qr_window_name)

    #
    # Camera management
    #

    def setup_camera_display(self, title: Optional[str] = None):
        self.create_window(self.camera_window_name, title=title)

    def teardown_camera_display(self):
        self.destroy_window(self.camera_window_name)

    def display_camera_image(self, image):
        cvimg = np.array(image)
        # RGB to BGR
        cvimg = cvimg[:, :, ::-1].copy()
        cv2.imshow(self.camera_window_name, cvimg)
        return window_is_open(self.camera_window_name, 100)

    #
    # Window management
    #

    def create_window(
        self,
        window_name: str,
        preserve_ratio: bool = False,
        title: Optional[str] = None,
    ):
        # The flags prevent the inclusion of a toolbar at the top or a
        # status bar at the bottom.
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)

        if preserve_ratio:
            cv2.setWindowProperty(
                window_name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO
            )

        # Resize & move the window
        cv2.resizeWindow(window_name, self.width, self.height)
        cv2.moveWindow(window_name, self.x_position, self.y_position)

        # Set the window title
        if title:
            cv2.setWindowTitle(window_name, title)

    def destroy_window(self, window_name):
        cv2.destroyWindow(window_name)

        # We need to wait at least 1 tick to give OpenCV time to
        # process the destroyWindow direction above.
        cv2.waitKey(1)
