__doc__ = """Hermit uses animated QR code sequences for input and output of data.

The functions in this module are used to:

* create QR code images from data or to parse data from QR code images

* split up data into pieces for a sequence of animated QR codes as
  well as reassemble pieces together into the original data

The Blockchain Commons UR protocol is used.

"""

from .create import (
    create_qr,
    create_qr_sequence,
    qr_to_image,
)
from .reassemblers import (
    GenericReassembler,
    BCURSingleReassembler,
    BCURMultiReassembler,
    SingleQRCodeReassembler,
)

from .detect import detect_qrs_in_image
