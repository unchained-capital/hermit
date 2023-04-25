from sys import stdin, argv
from os.path import basename

from hermit.qr import qr_to_image, create_qr

HELP = f"""usage: cat ... | python {basename(__file__)} OUTPUT_PATH

This program reads input text over STDIN and transforms it into an
image containing a QR code which it writes to OUTPUT_PATH."""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) != 2:
        print(HELP)
        exit(1)

    output_path = argv[1]
    data = stdin.read().strip()
    if len(data) == 0:
        print("Input data is required.")
        exit(2)

    qr_to_image(create_qr(data)).save(output_path)
