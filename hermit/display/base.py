from typing import Optional


class Display:
    """Base class for graphics display."""

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

    def animate_qrs(self, qrs: list) -> None:
        pass

    def format_qr(self, qr):
        pass

    def setup_camera_display(self, title: Optional[str] = None):
        pass

    def teardown_camera_display(self):
        pass

    def display_camera_image(self, image):
        pass
