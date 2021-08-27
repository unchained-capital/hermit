from .base import QRCamera
import imageio
from PIL import Image

class ImageIOCamera(QRCamera):
    def __init__(self):
        self.camera = None

    def open(self):
        if self.camera is None:
            self.camera = imageio.get_reader('<video0>')

    def get_image(self):
        image = None
        if self.camera is not None:
            frame = self.camera.get_next_data()
            image = Image.fromarray(frame)
        return image

    def close(self):
        if self.camera is not None:
            self.camera.close()
        self.camera = None
