from sys import argv

from pyzbar import pyzbar
from PIL import Image

from hermit.qrcode.format import decode_qr_code_data

HELP = """usage: python read_qr_code.py image.png

This program prints data from an image file containing a
Hermit-compatible QR code.

The data contained in the QR code will be unwrapped and uncompressed
before printing.
"""

if __name__ == '__main__':

    if ('--help' in argv) or ('-h' in argv) or len(argv) != 2:
        print(HELP)
        exit(1)

    input_path = argv[1]
    image = Image.open(input_path)
    for qrcode in pyzbar.decode(image):
        print(decode_qr_code_data(qrcode.data))
        break
