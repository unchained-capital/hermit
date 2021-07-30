from typing import Optional

from binascii import b2a_base64, a2b_base64
from pyzbar import pyzbar
import cv2
import re
from math import ceil

from prompt_toolkit import print_formatted_text
from .utils import window_is_open
from buidl.bcur import BCURMulti, BCURSingle

from .parser import QRParser, ParserException
from prompt_toolkit.shortcuts import ProgressBar



def read_qrs_in_frame(frame):
    """
    Return frame, [data_str1, data_str2, ...]

    The returned frame is the original frame with a green box
    drawn around each of the identified QR codes.
    """
    barcodes = pyzbar.decode(frame)

    # Mark the qr codes in the image
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

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

def read_qr_code(title=None) -> Optional[str]:
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
        print_formattrd_text(f"Error while parsing QRs: {pe.args[0]}")
        return None

    finally:
        # Clean up window stuff.
        print_formatted_text("Releasing camera and destorying window")
        cv2.destroyWindow(name)
        camera.release()

    return result_payload
