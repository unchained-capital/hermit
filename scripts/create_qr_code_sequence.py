from sys import stdin, argv
from os.path import basename

from hermit import qr_to_image, create_qr_sequence

HELP = f"""usage: cat ... | python {basename(__file__)} OUTPUT_PATH

This program reads input text over STDIN and transforms it into an
animation of a QR code sequence which it writes to OUTPUT_PATH."""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) != 2:
        print(HELP)
        exit(1)

    output_path = argv[1]
    data = stdin.read()
    if len(data) == 0:
        print("Input data is required.")
        exit(2)

    images = [qr_to_image(image) for image in create_qr_sequence(data=data)]
    print(f"Created {len(images)} QR code sequence.")

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        optimize=False,
        duration=200, # in milliseconds
        loop=0) # loop forever
