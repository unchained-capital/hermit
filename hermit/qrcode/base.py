import qrcode
from buidl.bcur import BCURMulti
from ..config import get_config
from typing import Optional
from .parser import QRParser, ParserException
from pyzbar import pyzbar
from prompt_toolkit import print_formatted_text
from PIL import Image, ImageOps
from PIL.ImageDraw import ImageDraw


class QRDisplay():
    def animate_qrs(self, qrs: list) -> None:
        pass

    def setup_camera_display(self):
        pass

    def teardown_camera_display(self):
        pass

    def display_camera_image(self, image):
        pass


class QRCamera():
    def open(self):
        pass

    def close(self):
        pass

    def get_image(self):
        pass


class QRSystem():
    def __init__(self, qr_config):
        camtype = qr_config.get('camera', 'opencv')
        if camtype == 'opencv':
            from .opencvcamera import OpenCVCamera
            self.camera = OpenCVCamera()
        elif camtype == 'imageio':
            from .imageiocamera import ImageIOCamera
            self.camera = ImageIOCamera()

        display = qr_config.get('display', 'opencv')
        if display == 'opencv':
            from .opencvqrdisplay import OpenCVQRDisplay
            self.display = OpenCVQRDisplay(qr_config)

        elif display == 'ascii':
            from .asciiqrdisplay import ASCIIQRDisplay
            self.display = ASCIIQRDisplay(qr_config)

        elif display == 'framebuffer':
            from .framebufferqrdisplay import FrameBufferQRDisplay
            self.display = FrameBufferQRDisplay(qr_config)

    def create_qr_code(self, data: str):
        version = 12
        fit = True  # otherwise gifs are of different sizes

        qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )
        qr.add_data(bytes(data, 'utf-8'))
        qr.make(fit=fit)
        return qr

        image = qr.make_image(fill_color="black", back_color="white")
        return image

    def display_qr_code(self, data: str) -> None:
        bc = BCURMulti(text_b64=data)
        chunks=bc.encode(animate=True)
        qrs = [self.create_qr_code(data) for data in chunks]

        return self.display.animate_qrs(qrs)

    def read_qrs_in_image(self, image, box_width=2):
        """
        Return frame, [data_str1, data_str2, ...]

        The returned frame is the original frame with a green box
        drawn around each of the identified QR codes.
        """
        barcodes = pyzbar.decode(image)

        annotate = ImageDraw(image)

        # Mark the qr codes in the image
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            annotate.rectangle([(x,y),(x+w,y+h)], outline="#00FF00", width=box_width)

        # Return the mirror image of the annoted original
        mirror = ImageOps.mirror(image)

        # Extract qr code data
        results = [
            barcode.data.decode("utf-8").strip()
            for barcode in barcodes
        ]

        return mirror, results


    def read_qr_code(self) -> Optional[str]:
        # Start the video capture
        self.camera.open()
        self.parser = QRParser()

        self.display.setup_camera_display()

        try:
            while not self.parser.is_complete():
                image = self.camera.get_image()
                mirror, data = self.read_qrs_in_image(image, box_width=20)

                if not self.display.display_camera_image(mirror):
                    break

                # Iterate through the identified qr codes and
                # parse them.
                for data_item in data:
                    message = self.parser.parse(data_item)

                #await asyncio.sleep(0.05)

            result_payload = self.parser.decode()

        except ParserException as pe:
            print_formatted_text(f"Error while parsing QRs: {pe.args[0]}")
            return None

        finally:
            # Clean up window stuff.
            self.display.teardown_camera_display()
            self.camera.close()

        return result_payload


_qr_system = None

def get_qr_system():
    global _qr_system

    if _qr_system is None:
        qr_config = get_config().qr_system
        _qr_system = QRSystem(qr_config)

    return _qr_system
