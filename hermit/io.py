from base64 import b64decode
from typing import Optional

from prompt_toolkit import print_formatted_text
from prompt_toolkit.shortcuts import ProgressBar

from .errors import (
    HermitError,
    InvalidQRCodeSequence,
)
from .config import get_config
from .qr import (
    create_qr_sequence,
    detect_qrs_in_image,
    GenericReassembler,
)

def display_data_as_animated_qrs(data: str) -> None:
    io = get_io()
    io.display_data_as_animated_qrs(data)
    
def read_data_from_animated_qrs() -> Optional[str]:
    io = get_io()
    return io.read_data_from_animated_qrs()

_io = None

def get_io() -> "IO":
    global _io

    if _io is None:
        io_config = get_config().io
        _io = IO(io_config)

    return _io

class IO():

    def __init__(self, io_config):

        camera_mode = io_config.get('camera', 'opencv')
        if camera_mode == 'opencv':
            from .camera.opencv import OpenCVCamera
            self.camera = OpenCVCamera()
        elif camera_mode == 'imageio':
            from .camera.imageio import ImageIOCamera
            self.camera = ImageIOCamera()
        else:
            raise HermitError(f"Invalid camera mode '{camera_mode}'.  Must be either 'opencv' or 'imageio'.")

        display_mode = io_config.get('display', 'opencv')
        if display_mode == 'opencv':
            from .display.opencv import OpenCVDisplay
            self.display = OpenCVDisplay(io_config)
        elif display_mode == 'framebuffer':
            from .display.framebuffer import FrameBufferDisplay
            self.display = FrameBufferDisplay(io_config)
        elif display_mode == 'ascii':
            from .display.ascii import ASCIIDisplay
            self.display = ASCIIDisplay(io_config)
        else:
            raise HermitError(f"Invalid display mode '{display_mode}'.  Must be one of 'opencv', 'framebuffer', or 'ascii'.")

    def display_data_as_animated_qrs(self, data:Optional[str]=None, base64_data:Optional[bytes]=None) -> None:
        return self.display.animate_qrs(create_qr_sequence(data=data, base64_data=base64_data))

    def read_data_from_animated_qrs(self, title:Optional[str]=None) -> Optional[str]:
        if title is None:
            title = "Scan QR Codes"

        self.camera.open()
        self.display.setup_camera_display(title)
        self.reassembler = GenericReassembler()

        data = FakeIterable(self)

        with ProgressBar(title=title) as progress_bar:
            try:
                while not self.reassembler.is_complete():
                    image = self.camera.get_image()
                    mirror, data = detect_qrs_in_image(image, box_width=20)

                    if not self.display.display_camera_image(mirror):
                        break

                    # Iterate through the identified QR codes and let the
                    # reassembler collect them.
                    for data_item in data:
                        total, segments = self.reassembler.collect(data_item)
                        if segments == 1:
                            progress_bar(
                                data, 
                                label="Scanning",
                                remove_when_done=True)
                                total=total)

                    #await asyncio.sleep(0.05)

                base64_payload = self.reassembler.decode()

            except InvalidQRCodeSequence as e:
                print_formatted_text(f"Invalid QR code sequence: {e}.")
                return None

            finally:
                # Clean up window stuff.
                self.display.teardown_camera_display()
                self.camera.close()

        return b64decode(base64_payload)

class FakeIterable(object):

    def __init__(self, reassembler):
        self.reassembler

    def __next__(self):
        if self.reassembler.is_complete():
            raise StopIteration
        else:
            yield self.context

        

    
