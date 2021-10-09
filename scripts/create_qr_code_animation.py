from sys import stdin, argv
from os.path import basename

from hermit import (
    get_config,
    qr_to_image,
    create_qr_sequence,
)

HELP = f"""usage: cat ... | python {basename(__file__)} OUTPUT_PATH [IS_BASE_64]

This program reads input text over STDIN and transforms it into an
animation of a QR code sequence which it writes to OUTPUT_PATH.

If IS_BASE_64 is not blank, the input data will be interpreted as an
already base64-encoded string."""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) not in (2, 3):
        print(HELP)
        exit(1)

    output_path = argv[1]
    data = stdin.read().strip()
    is_base64 = len(argv) == 3
    if len(data) == 0:
        print("Input data is required.")
        exit(2)

    if is_base64:
        sequence = create_qr_sequence(base64_data=data)
    else:
        sequence = create_qr_sequence(data=data)
    images = [qr_to_image(image) for image in sequence]
    print(
        f"Created {len(images)} image QR code sequence from {'base64' if is_base64 else 'plain'} input text."
    )

    qr_code_sequence_delay_ms = get_config().io["qr_code_sequence_delay"]

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        optimize=False,
        duration=qr_code_sequence_delay_ms,
        loop=0,
    )  # loop forever
