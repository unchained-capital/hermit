from os.path import basename
from sys import argv
from hermit import read_data_from_animated_qrs

HELP = f"""usage: python {basename(__file__)}

This program reads an animated sequence of QR images from the camera
and prints the data it contains."""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) != 1:
        print(HELP)
        exit(1)

    data = read_data_from_animated_qrs()
    print(data)
