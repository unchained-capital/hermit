from sys import stdin, argv
import base64
from buidl.bcur import BCURMulti
from hermit.qrcode import displayer

HELP = """usage: cat ... | python create_qr_code.py

This program reads input data over STDIN and transforms it into an
image containing a hermit compatible QR code, which it displays.
"""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) != 2:
        print(HELP)
        exit(1)

    data = stdin.read()
    encoded=base64.b64encode(data)
    displayer.display_qr_code(encoded, name="Jack")
