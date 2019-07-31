from sys import stdin, argv

from hermit.qrcode.displayer import create_qr_code_image

HELP = """usage: cat ... | python create_qr_code.py image.png

This program reads input data over STDIN and transforms it into an
image file containing a Hermit-compatible QR code.

The data contained in the QR code will be a wrapped & compressed
version of the input data.
"""

if __name__ == '__main__':

    if ('--help' in argv) or ('-h' in argv) or len(argv) != 2:
        print(HELP)
        exit(1)
        
    output_path = argv[1]
    data = stdin.read()
    image = create_qr_code_image(data)
    image.save(open(output_path, 'wb'))
