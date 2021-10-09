from base64 import b64encode
from typing import Optional
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_L
from buidl.bcur import BCURMulti

from ..errors import HermitError

# FIXME -- get these from config?
VERSION = 12
BOX_SIZE = 5
BORDER = 4

def create_qr_sequence(data:Optional[str]=None, base64_data:Optional[bytes]=None) -> [QRCode]:
    """Returns a BCUR Multi QR code sequence for the given `data` (or `base64_data`).

    If `data` is given, it will be UTF8 & base64 encoded first.  If
    `base64_data` is given, it will be used directly.

    If both `data` and `base64_data` are given, then `base64_data` will be used.

    """
    if base64_data is None:
        if data is None:
            raise HermitError("Must provide some `data` to create a QR code sequence.")
        else:
            base64_data = b64encode(data.encode("utf8"))
    return [
        create_qr(data)
        for data
        in BCURMulti(text_b64=base64_data).encode(animate=True)
    ]

def qr_to_image(qr: QRCode):
    """Turn the given `QRCode` into an image object, of the type returned
by `PIL.Image.open`."""
    # FIXME -- get colors from config?
    return qr.make_image(fill_color="black", back_color="white")

def create_qr(data: str) -> QRCode:
    """Returns a `QRCode` object representing the given `data`.

    In order to be displayed, this `QRCode` object will need to be
    further transformed, depending on the display mode.

    """
    qr = QRCode(
        version=VERSION,
        error_correction=ERROR_CORRECT_L,
        box_size=BOX_SIZE,
        border=BORDER,
    )
    qr.add_data(bytes(data, 'utf-8'))

    # otherwise gifs are of different sizes
    qr.make(fit=True)
    return qr
