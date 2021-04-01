from typing import Optional

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
    if len(bcur_parts) != 4:
        return None, None, None, None, "Doesn't have 3 slashes"

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

    if len(checksum) != 58:
        return None, None, None, None, "checksum must be 58 chars"

    if not uses_only_bech32_chars(checksum):
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
    print_formatted_text("starting loop")
    for barcode in barcodes:
        print_formatted_text("this is 1 frame")
        x, y , w, h = barcode.rect
        qrcode_data = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
 
        print_formatted_text("FOUND", qrcode_data)
        x_int, y_int, checksum, payload, err_msg = parse_bcur(qrcode_data)
        if err_msg:
            return {}, f"Invalid blockchain commons universal resource format v1:\n{err_msg}"

        print_formatted_text("before")
        decoded = bcur_decode(data=payload, checksum=checksum)  # TODO: NEEDS b2a_base64(enc).strip().decode() ?
        print_formatted_text("after")

        single_qr_dict = {
            "x_int": x_int,
            "y_int": y_int,
            "checksum": checksum,
            "payload": payload,
            "decoded": decoded,
        }

        print_formatted_text(f"returing single {single_qr_dict}...")
        return single_qr_dict, ""

    return {}, "No qr found"


def read_qr_code() -> Optional[str]:
    # Some useful info about pyzbar:
    # https://towardsdatascience.com/building-a-barcode-qr-code-reader-using-python-360e22dfb6e5

    qrs_array = []
    psbt_b64 = ''

    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()  # can delete this line?

    print_formatted_text("Kicking off outer loop")
    # need to do a lot of iterative processing to gather QR gifs and assemble them into one payload, so this is a bit complex
    while psbt_b64 == '':
        ret, frame = camera.read()
        single_qr_dict, err_msg = read_single_qr(frame)

        #TODO mirror-flip the image?
        mirror = cv2.flip(frame, 1)
        cv2.imshow("Scan the PSBT You Want to Sign", mirror)
        if err_msg:
            print_formatted_text("red")
            print_formatted_text(err_msg)
            continue

        print_formatted_text("We made it htis far")

        # First time we've scanned a QR gif, initializing the result array
        if qrs_array == []:
            qrs_array = [None for _ in range(single_qr_dict["y_int"])]

        if qrs_array[single_qr_dict["x_int"]-1] is None:
            print_formatted_text("Already scanned this QR, ignore")
        else:
            print_formatted_text("Adding to array")  # TODO: NEEDS b2a_base64(enc).strip().decode() ?
            qrs_array[single_qr_dict["x_int"]-1] = single_qr_dict["payload"]

        if cv2.waitKey(1) & 0xFF == 27:
            break

        # TODO: something more performant?
        if None not in qrs_array:
            psbt_b64 = ".".join(qrs_array)
            print_formatted_text("Finalizing PSBT", psbt_b64)

    if psbt_b64:
        # need the if clause in case of user escaping
        try:
            # This will throw an error if it's a valid QR but not a valid PSBT
            PSBT.parse_base64(psbt_b64)
        except Exception as e:
            print_formatted_text("PSBT Decode Error:", e)
            print_formatted_text("Original PSBT:", psbt_b64)
            raise(e)  # TODO: better error handling

    print_formatted_text("Releasing camera and destorying window")
    camera.release()
    cv2.destroyWindow()

    print_formatted_text("Returning outer loop")
    return psbt_b64
