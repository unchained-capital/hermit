from sys import stdin, argv
from os.path import basename

from buidl import PSBT


HELP = f"""usage: cat ... | python {basename(__file__)}

This program reads a PSBT (in base64) over STDIN, reads it into
buidl and prints the resulting PSBT in connonical order.
"""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) != 1:
        print(HELP)
        exit(1)

    raw_unsigned_psbt_base64 = stdin.read().strip()
    if len(raw_unsigned_psbt_base64) == 0:
        print("Input PSBT is required.")
        exit(2)

    psbt = PSBT.parse_base64(raw_unsigned_psbt_base64)

    print(psbt.serialize_base64())
