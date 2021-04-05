from typing import Optional

from binascii import b2a_base64
from pyzbar import pyzbar
import cv2
import re

from buidl import PSBT
from buidl.bech32 import bcur_decode

from prompt_toolkit import print_formatted_text  # FIXME


# TODO: move some of this to buidl?


HEX_CHARS_RE = re.compile('^[0-9a-f]*$')
BECH32_CHARS_RE = re.compile("^[qpzry9x8gf2tvdw0s3jn54khce6mua7l]*$")


def uses_only_hex_chars(string):
    return bool(HEX_CHARS_RE.match(string.lower()))


def uses_only_bech32_chars(string):
    return bool(BECH32_CHARS_RE.match(string.lower()))


def _is_intable(int_as_string):
    # TODO: move me to a util/helper library somewhere
    try:
        int(int_as_string)
        return True
    except Exception:
        return False


def parse_bcur(string):
    """
    Returns x, y, checksum, payload, err_msg
    """

    string = string.upper().strip()
    if not string.startswith("UR:BYTES/"):
        return None, None, None, None, "Doesn't start with UR:BYTES/"

    bcur_parts = string.split("/")
    if len(bcur_parts) == 2:
        # Non-animated QR code (just 1 qr, doesn't display 1of1 nor checksum)
        _, payload = bcur_parts
        checksum, x_int, y_int = None, 1, 1
    elif len(bcur_parts) == 4:
        # Animated QR code
        _, xofy, checksum, payload = bcur_parts

        xofy_parts = xofy.split("OF")
        if len(xofy_parts) != 2:
            return None, None, None, None, "xOFy section malformed"

        if not _is_intable(xofy_parts[0]) or not _is_intable(xofy_parts[1]):
            return None, None, None, None, f"y in xOFy must be an integer: {xofy_parts}"

        x_int = int(xofy_parts[0])
        y_int = int(xofy_parts[1])

        if x_int > y_int: 
            return None, None, None, None, "x must be >= y (in xOFy)"
    else:
        return None, None, None, None, "Doesn't have 3-4 slashes"

    if checksum and len(checksum) != 58:
        return None, None, None, None, "checksum must be 58 chars"

    if checksum and not uses_only_bech32_chars(checksum):
        return None, None, None, None, f"checksum can only contain bech32 characters: {checksum}"

    if not uses_only_bech32_chars(payload):
        return None, None, None, None, f"payload can only contain bech32 characters: {payload}"

    return x_int, y_int, checksum, payload, ""


def read_single_qr(frame):
    """
    Return frame, single_qr_dict, err_msg
    """
    barcodes = pyzbar.decode(frame)
    # we don't know how many QRs we'll need until the scanning begins, so initialize as none
    for barcode in barcodes:
        x, y , w, h = barcode.rect
        qrcode_data = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
 
        print_formatted_text("FOUND", qrcode_data)
        x_int, y_int, checksum, payload, err_msg = parse_bcur(qrcode_data)
        if err_msg:
            return {}, f"Invalid blockchain commons universal resource format v1:\n{err_msg}"

        single_qr_dict = {
            "x_int": x_int,
            "y_int": y_int,
            "checksum": checksum,
            "payload": payload,
        }

        print_formatted_text(f"returing single {single_qr_dict}...")
        return frame, single_qr_dict, ""

    return frame, {}, "No qr found"


def read_qr_code() -> Optional[str]:
    # Some useful info about pyzbar:
    # https://towardsdatascience.com/building-a-barcode-qr-code-reader-using-python-360e22dfb6e5

    # FIXME: get rid of all the debug prints in here

    # initialize variables
    qrs_array = []
    psbt_checksum, psbt_payload = '', ''

    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()  # can delete this line?

    # need to do a lot of iterative processing to gather QR gifs and assemble them into one payload, so this is a bit complex
    print_formatted_text("Starting QR code scanner (window should pop-up)...")
    while True: 
        if qrs_array:
            num_scanned = len([x for x in qrs_array if x is not None])
            print_formatted_text(f"Scanned {num_scanned} of {len(qrs_array)} QRs")

        ret, frame = camera.read()

        frame, single_qr_dict, err_msg = read_single_qr(frame)

        # Mirror-flip the image for UI
        mirror = cv2.flip(frame, 1)
        cv2.imshow("Scan the PSBT You Want to Sign", mirror)
        if cv2.waitKey(1) & 0xFF == 27:
            # Unclear why this line matters, but if we don't include this immediately after `imshow` then then the scanner preview won't display (on macOS):
            break

        if err_msg:
            if err_msg != "No qr found":
                # Otherwise we get constant errors for tons of frames where the scanner doesn't see QR code
                print_formatted_text("PSBT scan error:" + err_msg)
            continue

        # First time we've scanned a QR gif, initializing the results array and checksum
        if qrs_array == []:
            qrs_array = [None for _ in range(single_qr_dict["y_int"])]
            checksum = single_qr_dict["checksum"]

        if qrs_array[single_qr_dict["x_int"]-1] is None:
            print_formatted_text("Adding to array")
            qrs_array[single_qr_dict["x_int"]-1] = single_qr_dict["payload"]
        else:
            print_formatted_text(f"Already scanned QR #{single_qr_dict['x_int']}, ignoring")

        # TODO: something more performant?
        if None not in qrs_array:
            psbt_payload = "".join(qrs_array)
            print_formatted_text("Finalizing PSBT payload", psbt_payload)
            break

    print_formatted_text("Releasing camera and destorying window")
    camera.release()
    # For some reason, this breaks the hermit UI?:
    # cv2.destroyWindow()

    # TODO: better/consistent error handling on all these failure cases

    if not psbt_payload:
        # need the if clause in case of user escaping during QR scanning
        # TODO: streamline control logic to avoid this if statement?
        return

    try:
        enc = bcur_decode(data=psbt_payload, checksum=checksum)
        psbt_b64 = b2a_base64(enc).strip().decode()
    except Exception as e:
        print_formatted_text(f"Invalid PSBT: {e}")
        return

    try:
        # This will throw an error if it's a valid QR payload but not a valid PSBT
        PSBT.parse_base64(psbt_b64)
        print_formatted_text(f"PSBT {psbt_b64} successfully parsed")
        return psbt_b64
    except Exception as e:
        print_formatted_text("PSBT Decode Error:", e)
        print_formatted_text("Original PSBT:", psbt_b64)
        raise(e)
