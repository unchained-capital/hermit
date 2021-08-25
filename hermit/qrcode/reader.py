from typing import Optional
from binascii import b2a_base64, a2b_base64
from pyzbar import pyzbar
import cv2
import re
from math import ceil
from PIL import Image, ImageEnhance, ImageOps
from colors import color

import time

from prompt_toolkit import print_formatted_text, ANSI
from prompt_toolkit.shortcuts import clear
from .utils import window_is_open
from buidl.bcur import BCURMulti, BCURSingle

from .parser import QRParser, ParserException
from prompt_toolkit.shortcuts import ProgressBar

from .framebuffer import write_image_to_fb, copy_image_from_fb


def read_qrs_in_frame(frame, box_width=2):
    """
    Return frame, [data_str1, data_str2, ...]

    The returned frame is the original frame with a green box
    drawn around each of the identified QR codes.
    """
    barcodes = pyzbar.decode(frame)

    # Mark the qr codes in the image
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), box_width)

    # Extract qr code data
    results = [
        barcode.data.decode("utf-8").strip()
        for barcode in barcodes
    ]

    return frame, results

# This method handles reading QR codes from the camera and
# parses the results looking for vaious mulit-part QR encodings.
# If it finds one, it attempts to load the full data payload, and
# displays a handy progress bar giving the user some feedback about
# how many segments are left to read.

def old_read_qr_code(title=None) -> Optional[str]:
    if title is None:
        title = "Scan the barcode."

    name = "readqr"

    # Dont include a toolbar or a status bar at the bottom.
    cv2.namedWindow(name, cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)

    # Change the title
    cv2.setWindowTitle(name, title)

    # Move the window to a sane place on the screen
    cv2.moveWindow(name, 100, 100)

    # Start the video capture
    camera = cv2.VideoCapture(0)
    parser = QRParser()

    # need to do a lot of iterative processing to gather QR gifs and assemble them into one payload, so this is a bit complex
    print_formatted_text("Starting QR code scanner (window should pop-up)...")

    try:
        with ProgressBar() as pb:
            progress_bar_counter = pb()

            while not parser.is_complete():
                ret, frame = camera.read()
                frame, data = read_qrs_in_frame(frame)
                mirror = cv2.flip(frame, 1)
                cv2.imshow(name, mirror)

                # Quit the loop if someone hits a key, or closes
                # the camera winow
                if not window_is_open(name, 100):
                    break

                # Iterate through the identified qr codes and
                # parse them.
                for data_item in data:
                    message = parser.parse(data_item)

                    # Parse returns something non-None when it
                    # sees a new value
                    if message is not None:
                        if parser.total is not None:
                            progress_bar_counter.total = parser.total
                        progress_bar_counter.label = f"{parser.type} {message}"
                        progress_bar_counter.current += 1

        result_payload = parser.decode()

    except ParserException as pe:
        print_formatted_text(f"Error while parsing QRs: {pe.args[0]}")
        return None

    finally:
        # Clean up window stuff.
        print_formatted_text("Releasing camera and destorying window")
        cv2.destroyWindow(name)
        camera.release()

    return result_payload

class Ansi:
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


def render(cv2_image, width=120, height_scale=0.55, colorize=True):
    img = Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    org_width, orig_height = img.size
    aspect_ratio = orig_height / org_width
    new_height = aspect_ratio * width * height_scale
    img = img.resize((width, int(new_height)))
    img = img.convert('RGBA')
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    pixels = img.getdata()
    def mapto(r, g, b, alpha):
        if alpha == 0.:
            return ' '
        chars = ["B", "S", "#", "&", "@", "$", "%", "*", ":", ".", " "]
        pixel = (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16
        if colorize:
            return Ansi.color(chars[pixel // 25], r, g, b)
        else:
            return chars[pixel // 25]
    new_pixels = [mapto(r, g, b, alpha) for r, g, b, alpha in pixels]
    new_pixels_count = len(new_pixels)
    ascii_image = [''.join(new_pixels[index:index + width]) for index in range(0, new_pixels_count, width)]
    ascii_image = "\n".join(ascii_image)
    return ascii_image

def read_qr_code(title=None) -> Optional[str]:
    # Start the video capture
    camera = cv2.VideoCapture(0)
    parser = QRParser()

    saved = None

    try:
        while not parser.is_complete():
            ret, frame = camera.read()
            frame, data = read_qrs_in_frame(frame, box_width=20)
            mirror = cv2.flip(frame, 1)

            if saved is None:
                saved = copy_image_from_fb(-100,100, len(mirror[0]), len(mirror) )

            #ascii = render(mirror, width=80, height_scale=0.45)
            #clear()
            #print_formatted_text(ANSI(ascii))
            image = Image.fromarray(mirror)
            write_image_to_fb(-100, 100, image)


            # Iterate through the identified qr codes and
            # parse them.
            for data_item in data:
                message = parser.parse(data_item)

            #await asyncio.sleep(0.05)

        result_payload = parser.decode()

    except ParserException as pe:
        print_formattrd_text(f"Error while parsing QRs: {pe.args[0]}")
        return None

    finally:
        # Clean up window stuff.
        if saved is not None:
            write_image_to_fb(-100,100,saved)

        print_formatted_text("Releasing camera and destorying window")
        camera.release()

    return result_payload
