from typing import Optional

from binascii import b2a_base64, a2b_base64
from pyzbar import pyzbar
import cv2
import re
from math import ceil

from buidl import PSBT

from prompt_toolkit import print_formatted_text  # FIXME

def parse_specter_desktop_qr(qrcode_data):
    """
    returns payload, x_int, y_int
    """
    parts = qrcode_data.split(" ")
    if len(parts) == 1:
        # it's just 1 chunk of data, no encoding of any kind
        return qrcode_data, 1, 1
    elif len(parts) == 2:
        xofy, payload = parts
        # xofy might look like p2of4
        xofy_re = re.match("p([0-9]*)of([0-9]*)", xofy)
        if xofy_re is None:
            raise ValueError(f"Invalid QR payload: {qrcode_data}")
        # safe to int these because we know from the regex that they're composed of ints only:
        print_formatted_text('xofy', xofy)
        print_formatted_text('xofy_re', xofy_re)
        x_int = int(xofy_re[1])
        y_int = int(xofy_re[2])
        return payload, x_int, y_int
    else:
        raise ValueError(f"Invalid QR payload: {qrcode_data}")
        

def read_single_qr(frame):
    """
    Return frame, single_qr_dict
    """
    barcodes = pyzbar.decode(frame)
    # we don't know how many QRs we'll need until the scanning begins, so initialize as none
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        qrcode_data = barcode.data.decode("utf-8")
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        print_formatted_text("FOUND", qrcode_data)
        # At this point we don't know if it's single or part of a multi, and if multi we don't have all the pieces to parse
        # If this throws a ValueError it will be handled by the caller
        payload, x_int, y_int = parse_specter_desktop_qr(qrcode_data)

        single_qr_dict = {
            "x_int": x_int,
            "y_int": y_int,
            "payload": payload,
        }

        print_formatted_text(f"returing single {single_qr_dict}...")
        return frame, single_qr_dict

    return frame, {}


def read_qr_code() -> Optional[str]:
    # Some useful info about pyzbar:
    # https://towardsdatascience.com/building-a-barcode-qr-code-reader-using-python-360e22dfb6e5

    # FIXME: get rid of all the debug prints in here

    # initialize variables
    qrs_array = []
    psbt_checksum, psbt_payload = "", ""

    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()  # can delete this line?

    # need to do a lot of iterative processing to gather QR gifs and assemble them into one payload, so this is a bit complex
    print_formatted_text("Starting QR code scanner (window should pop-up)...")
    while True:
        # Mirror-flip the image for UI
        mirror = cv2.flip(frame, 1)
        cv2.imshow("Scan the PSBT You Want to Sign", mirror)
        if cv2.waitKey(1) & 0xFF == 27:
            # Unclear why this line matters, but if we don't include this immediately after `imshow` then then the scanner preview won't display (on macOS):
            break

        if qrs_array:
            num_scanned = len([x for x in qrs_array if x is not None])
            print_formatted_text(f"Scanned {num_scanned} of {len(qrs_array)} QRs")

        ret, frame = camera.read()

        try:
            frame, single_qr_dict = read_single_qr(frame)

        except ValueError as e:
            print_formatted_text(f"QR Scan Error:\n{e}")
            continue

        if not single_qr_dict:
            # No qr found
            continue

        print_formatted_text(f"Found {single_qr_dict}")

        # First time we've scanned a QR gif we initialize the results array
        if qrs_array == []:
            qrs_array = [None for _ in range(single_qr_dict["y_int"])]

        if qrs_array[single_qr_dict["x_int"] - 1] is None:
            print_formatted_text("Adding to array")
            qrs_array[single_qr_dict["x_int"] - 1] = single_qr_dict["payload"]
        else:
            print_formatted_text(
                f"Already scanned QR #{single_qr_dict['x_int']}, ignoring"
            )

        # TODO: something more performant?
        if None not in qrs_array:
            psbt_payload = "".join(qrs_array)
            print_formatted_text("Finalizing PSBT payload", psbt_payload)
            break

    print_formatted_text("Releasing camera and destorying window")
    camera.release()
    # For some reason, this breaks the hermit UI?:
    # cv2.destroyWindow()

    return psbt_payload

    if False:
        # FIXME
        # Confirm this is OK. psbt_payload initialized as "" but this is returning None (better?)
        if not psbt_payload:
            # need the if clause in case of user escaping during QR scanning
            # TODO: streamline control logic to avoid this if statement?
            return
