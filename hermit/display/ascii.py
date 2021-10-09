from io import StringIO
from time import sleep

from qrcode import QRCode
from prompt_toolkit import print_formatted_text,ANSI
from prompt_toolkit.shortcuts import clear
from PIL import Image, ImageEnhance

from .base import Display

class ANSIColorMap:
    """This class has some quick and dirty mappings from 24bit color space
    to 16-color ansi terminal space.

    """

    Reset = '\u001b[0m'
    Home = '\u001b[1;1H'
    Clear = '\u001b[2J'

    Black = '\u001b[30m'
    Red = '\u001b[31m'
    Green = '\u001b[32m'
    Yellow = '\u001b[33m'
    Blue = '\u001b[34m'
    Magenta = '\u001b[35m'
    Cyan = '\u001b[36m'
    White = '\u001b[37m'
    BrightBlack = '\u001b[30;1m'
    BrightRed = '\u001b[31;1m'
    BrightGreen = '\u001b[32;1m'
    BrightYellow = '\u001b[33;1m'
    BrightBlue = '\u001b[34;1m'
    BrightMagenta = '\u001b[35;1m'
    BrightCyan = '\u001b[36;1m'
    BrightWhite = '\u001b[37;1m'


    RGB2Bit = [
        [ # red 00
            [ Black, Black, Blue, Blue ], # Green 00
            [ Black, Black, Blue, Blue ], # Green 01
            [ Green, Green, Cyan, Cyan ], # Green 10
            [ Green, Green, Cyan, Cyan ], # Green 11
        ],

        [ # red 01
            [ Black, Black, Blue, Blue ], # Green 00
            [ Black, BrightBlack, BrightBlue, BrightBlue ], # Green 01
            [ Green, BrightGreen, Cyan, Cyan ], # Green 10
            [ Green, BrightGreen, Cyan, BrightCyan ], # Green 11
        ],

        [ # red 10
            [ Red, Red, Magenta, Magenta ], # Green 00
            [ Red, Red, Magenta, Magenta ], # Green 01
            [ Yellow, Yellow, White, White ], # Green 10
            [ Yellow, Yellow, White, BrightCyan ], # Green 11
        ],

        [ # red 11
            [ Red, Red, Magenta, Magenta ], # Green 00
            [ Red, BrightRed, BrightMagenta, White ], # Green 01
            [ Yellow, BrightYellow, White, BrightWhite ], # Green 10
            [ Yellow, White, BrightWhite, BrightWhite ], # Green 11
        ],
    ]

    @classmethod
    def color(self, char,r,g,b):
        r = r//64
        g = g//64
        b = b//64
        return self.RGB2Bit[r][g][b] + char + self.Reset


class ASCIIDisplay(Display):

    DEFAULT_WIDTH = 80

    def __init__(self, io_config):
        Display.__init__(self, io_config)

        # FIXME This is undocumented in config.py
        self.height_scale = float(io_config.get('height_scale', 0.45))

    #
    # Displaying QRs
    #

    def format_qr(self, qr: QRCode) -> str:
        f = StringIO()
        qr.print_ascii(f)
        return f.getvalue()

    def animate_qrs(self, qrs: list) -> None:
        ascii_images = [self.format_qr(qr) for qr in qrs]

        total = len(ascii_images)
        finished = False
        while not finished:
            for index, image in enumerate(ascii_images):
                clear()
                print_formatted_text(ANSI(image))
                sleep(self.qr_code_sequence_delay_seconds)

    #
    # Camera management
    #

    def display_camera_image(self, image):
        ascii = self.render(image, width=self.width, height_scale=self.height_scale)
        clear()
        print_formatted_text(ANSI(ascii))
        return True

    def render(self, image, width=120, height_scale=0.55, colorize=True):
        org_width, orig_height = image.size
        aspect_ratio = orig_height / org_width
        new_height = aspect_ratio * width * height_scale
        img = image.resize((width, int(new_height)))
        img = img.convert('RGBA')
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        pixels = img.getdata()
        def mapto(r, g, b, alpha):
            if alpha == 0.:
                return ' '
            chars = ["B", "S", "#", "&", "@", "$", "%", "*", ":", ".", " "]
            pixel = (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16
            return ANSIColorMap.color(chars[pixel // 25], r, g, b)

        new_pixels = [mapto(r, g, b, alpha) for r, g, b, alpha in pixels]
        new_pixels_count = len(new_pixels)
        ascii_image = [''.join(new_pixels[index:index + width]) for index in range(0, new_pixels_count, width)]
        ascii_image = "\n".join(ascii_image)
        return ascii_image
