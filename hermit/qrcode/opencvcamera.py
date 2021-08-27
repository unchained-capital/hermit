from .base import QRCamera
from PIL import Image
import cv2

class OpenCVCamera(QRCamera):
    def __init__(self):
        self.camera = None

    def open(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)

    def get_image(self):
        image = None
        if self.camera is not None:
            ret, frame = self.camera.read()
            bgr = Image.fromarray(frame)
            b,g,r = bgr.split()
            image = Image.merge("RGB", (r,g,b))
        return image

    def close(self):
        if self.camera is not None:
            self.camera.release()
        self.camera = None

