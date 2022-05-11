from typing import Optional
from .base import Camera
from PIL import Image

try:
    from imageio import get_reader
except ModuleNotFoundError:
    print("ERROR: imageio library not installed")


class ImageIOCamera(Camera):
    """Corresponds to camera mode ``imageio``.

    Uses the `ImageIO <https://imageio.readthedocs.io/en/stable/>`_
    library.

    Allows getting high-resolution image data from the web camera
    despite not having a graphical environment.

    """

    def __init__(self):
        self.camera = None

    def open(self):
        if self.camera is None:
            self.camera = get_reader("<video0>")

    def get_image(self) -> Optional[Image.Image]:
        image = None
        if self.camera is not None:
            frame = self.camera.get_next_data()
            image = Image.fromarray(frame)
        return image

    def close(self):
        if self.camera is not None:
            self.camera.close()
        self.camera = None
