from io import BytesIO
from time import sleep
from typing import Optional, List

from qrcode import QRCode
from PIL import Image
import FBpyGIF.fb as fb

from ..qr import qr_to_image
from .base import Display


def copy_image_from_fb(x, y, w, h):
    (mm, fbw, fbh, bpp) = fb.ready_fb()
    bytespp = bpp // 8
    s = w * bytespp

    # Allow negative x and y to place image from the right or bottom
    if x < 0:
        x = fbw + x - w

    if y < 0:
        y = fbh + y - h

    b = BytesIO()
    for z in range(h):
        fb.mmseekto(fb.vx + x, fb.vy + y + z)
        b.write(fb.mm.read(s))

    return Image.frombytes("RGBA", (w, h), b.getvalue())


def write_image_to_fb(x, y, image):
    w = image.width
    h = image.height

    (mm, fbw, fbh, bpp) = fb.ready_fb()
    bytespp = bpp // 8

    # Allow negative x and y to place image from the right or bottom
    if x < 0:
        x = fbw + x - w

    if y < 0:
        y = fbh + y - h

    bytespp = bpp // 8
    s = w * bytespp

    b = BytesIO(image.convert("RGBA").tobytes("raw", "RGBA"))

    for z in range(h):
        fb.mmseekto(fb.vx + x, fb.vy + y + z)
        fb.mm.write(b.read(s))


class FrameBufferDisplay(Display):
    """Corresponds to display mode ``framebuffer``.

    Displays data by directly writing to the display's framebuffer.

    This allows displaying images within a terminal.

    """

    #: Override the default horizontal position for frame buffers.
    DEFAULT_X_POSITION = -100

    #
    # Displaying QRs
    #

    def format_qr(self, qr: QRCode):
        return qr_to_image(qr).convert("RGBA")

    def animate_qrs(self, qrs: List[QRCode]) -> None:
        images = [self.format_qr(qr) for qr in qrs]

        if len(images) == 0:
            return

        saved = copy_image_from_fb(
            self.x_position, self.y_position, images[0].width, images[0].height
        )

        finished = False
        try:
            while not finished:
                for image in images:
                    write_image_to_fb(self.x_position, self.y_position, image)
                    sleep(self.qr_code_sequence_delay_seconds)
        finally:
            write_image_to_fb(self.x_position, self.y_position, saved)

    #
    # Camera management
    #

    def setup_camera_display(self, title: Optional[str] = None):
        self.saved = None

    def teardown_camera_display(self):
        if self.saved is not None:
            write_image_to_fb(self.x_position, self.y_position, self.saved)
            self.saved = None

    def display_camera_image(self, image):
        if self.saved is None:
            self.saved = copy_image_from_fb(
                self.x_position, self.y_position, image.width, image.height
            )

        r, g, b = image.split()
        bgr = Image.merge("RGB", (b, g, r))

        write_image_to_fb(self.x_position, self.y_position, bgr)
        return True
