from typing import Optional, List
from qrcode import QRCode
from PIL import Image


class Display:
    """Abstract base class for displays.

    For displaying sequences of animated QR codes, concrete subclasses
    should implement the ``animate_qrs`` method.

    For displaying what the camera sees, concrete subclasses should
    implement the ``display_camera_image`` method.

    ``setup_camera_display`` and ``teardown_camera_display`` methods
    are also available to aid with setup and teardown of resources
    associated with the display of the camera.

    """

    #: Default delay (in milliseconds) between successive QR codes in
    #: a sequence.
    DEFAULT_QR_CODE_SEQUENCE_DELAY = 200

    #: Default horizontal position for display.
    DEFAULT_X_POSITION = 100

    #: Default vertical position for display.
    DEFAULT_Y_POSITION = 100

    #: Default width for display.
    DEFAULT_WIDTH = 300

    #: Default height for display.
    DEFAULT_HEIGHT = 300

    def __init__(self, io_config: dict):
        self.x_position = int(io_config.get("x_position", self.DEFAULT_X_POSITION))
        self.y_position = int(io_config.get("y_position", self.DEFAULT_Y_POSITION))
        self.width = int(io_config.get("width", self.DEFAULT_WIDTH))
        self.height = int(io_config.get("height", self.DEFAULT_HEIGHT))
        self.qr_code_sequence_delay_ms = int(
            io_config.get("qr_code_sequence_delay", self.DEFAULT_QR_CODE_SEQUENCE_DELAY)
        )
        self.qr_code_sequence_delay_seconds = self.qr_code_sequence_delay_ms / 1000

    #
    # QR Code Animation
    #

    def animate_qrs(self, qrs: List[QRCode]) -> None:
        """Display the list of QR codes as an animated sequence."""
        pass

    #
    # Camera
    #

    def setup_camera_display(self, title: Optional[str] = None):
        """Initialize the display for the camera.

        If possible, the given ``title`` should be used to label the
        display (e.g. - the window in a graphical user interface).

        """
        pass

    def teardown_camera_display(self):
        """Tear down the display for the camera."""
        pass

    def display_camera_image(self, image: Image.Image):
        """Display the given ``image`` for the camera."""
        pass
