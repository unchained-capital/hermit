
from sys import argv
import base64
from buidl.bcur import BCURMulti
from hermit.qrcode import reader

HELP = """usage: python read_qr_code.py

This program prints data from an image file containing a
Hermit-compatible QR code.
"""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) != 2:
        print(HELP)
        exit(1)

    result = reader.read_qr_code()
    print(base64.b64decode(result).decode('utf-8'))
