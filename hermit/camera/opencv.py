from typing import Optional
from ..errors import HermitError
from .base import Camera
from PIL import Image

try:
    import cv2
except ModuleNotFoundError:
    print("ERROR: cv2 library not installed")


class OpenCVCamera(Camera):
    """Corresponds to camera mode ``opencv``.

    Uses the `OpenCV <https://opencv.org/>`_ library.

    Requires that Hermit is running in a graphical environment.

    """

    def __init__(self):
        self.camera = None

    def open(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise HermitError("Cannot open camera")

    def get_image(self) -> Optional[Image.Image]:
        image = None
        if self.camera is not None:
            ret, frame = self.camera.read()
            bgr = Image.fromarray(frame)
            b, g, r = bgr.split()
            image = Image.merge("RGB", (r, g, b))
        return image

    def close(self):
        if self.camera is not None:
            self.camera.release()
        self.camera = None
