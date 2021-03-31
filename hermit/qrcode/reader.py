from typing import Optional

from pyzbar import pyzbar
import cv2

from buidl import PSBT


# TODO: move some of this to buidl?


HEX_CHARS_RE = re.compile('^[0-9a-f]*$')

def uses_only_hex_chars(string):
    return bool(HEX_CHARS_RE.match(string))


def _is_intable(int_as_string):
    try:
        int(int_as_astring)
        return True
    except Exception:
        return False


def decode_bcur(string):
    """
    Returns x, y, checksum, payload, err_msg
    """

    string = string.upper()
    if not string.lower().startswith("UR:BYTES/"):
        return None, None, None, None, "Doesn't start with UR:BYTES/"

    bcur_parts = string.split("/")
    if len(parts) != 4:
        return None, None, None, None, "Doesn't have 3 slashes"

    _, xofy, checksum, msg = bcur_parts

    xofy_parts = xofy.split("OF")
    if len(xofy_parts) != 2:
        return None, None, None, None, "xOFy section malformed"

    if not _is_intable(xofy_parts[0]) or not _is_intable(xofy_parts[1]):
        return None, None, None, None, "xOFy must be integers"

    x_int = int(xofy_parts[0])
    y_int = int(xofy_parts[1])

    if x_int > y_int: 
        return None, None, None, None, "x must be >= y (in xOFy)"

    if len(checksum) != 58:
        return None, None, None, None, "checksum must be 58 chars"$a

    if not uses_only_hex_chars(checksum):
        return None, None, None, None, "checksum can only contain hexadecimal characters"

    if not uses_only_hex_chars(msg):
        return None, None, None, None, "Payload can only contain hexadecimal characters"

    return x_int, y_int, checksum, payload, ""


def read_qrs(frame):
    barcodes = pyzbar.decode(frame)
    num_qrs_needed = 1  # for QR gif
    qrs_array = []
    for barcode in barcodes:
        x, y , w, h = barcode.rect
        qrcode_data = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
 
        print("FOUND", qrcode_data)
        x_int, y_int, checksum, payload, err_msg = decode_bcur(qrcode_data)
        if err_msg:
            return frame, "", f"Invalid blockchain commons universal resource format v1 {err_msg}"

        if y_int > num_qrs_needed:
            num_qrs_needed = y_int

        decoded = bcur_decode(data=payload, checksum=checksum)

        print("Adding to array")
        qrs_array[x_int-1] = decoded

    if len(qrs_array) < num_qrs_needed:
        err_msg = f"Scanned {len(qrs_array)} but needed {num_qrs_needed} QR codes! Try scanning again."
        return frame, "", err_msg

    # Repackage qr gifs into one

    # This will throw an error if it's a valid QR but not a valid PSBT
    try:
        PSBT.parse_base64(qrcode_data)
    except Exception as e:
        print("PSBT Decode Error:", e)
        print("Original PSBT:", qrcode_data)
        return frame, qrcode_data, str(e)

    return frame, "", "Could not decode a valid QR code"


def read_qr_code() -> Optional[str]:
    # Some useful info about pyzbar:
    # https://towardsdatascience.com/building-a-barcode-qr-code-reader-using-python-360e22dfb6e5

    decoded_data = None
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()

    while ret:
        ret, frame = camera.read()  # TODO: DRY this out?
        frame, decoded_data, err_msg = read_qrs(frame)

        #TODO mirror-flip the image?
        mirror = cv2.flip(frame, 1)
        cv2.imshow("Scan the PSBT You Want to Sign", mirror)
        if decoded_data or cv2.waitKey(1) & 0xFF == 27:
            break

    camera.release()
    cv2.destroyWindow()
    return decoded_data
