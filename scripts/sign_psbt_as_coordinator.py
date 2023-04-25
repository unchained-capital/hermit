from sys import stdin, argv
from os.path import basename

from buidl import PSBT

from hermit.coordinator import (
    COORDINATOR_SIGNATURE_KEY,
    create_rsa_signature,
)

HELP = f"""usage: cat ... | python {basename(__file__)} PRIVATE_KEY_PATH

This program reads an unsigned PSBT (in base64) over STDIN, signs that
PSBT as a coordinator, and prints the resulting PSBT..

The RSA private key at PRIVATE_KEY_PATH is used for signing."""

if __name__ == "__main__":

    if ("--help" in argv) or ("-h" in argv) or len(argv) != 2:
        print(HELP)
        exit(1)

    private_key_path = argv[1]

    unsigned_psbt_base64 = stdin.read().strip()
    if len(unsigned_psbt_base64) == 0:
        print("Input PSBT is required.")
        exit(2)
    psbt = PSBT.parse_base64(unsigned_psbt_base64)

    message = unsigned_psbt_base64.encode("utf8")
    signature = create_rsa_signature(message, private_key_path)

    psbt.extra_map[COORDINATOR_SIGNATURE_KEY] = signature

    print(psbt.serialize_base64())
