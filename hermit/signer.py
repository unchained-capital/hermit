from decimal import Decimal
from typing import Optional, List

from prompt_toolkit import PromptSession, print_formatted_text, HTML
from buidl import PSBT

from .errors import HermitError, InvalidPSBT
from .io import (
    display_data_as_animated_qrs,
    read_data_from_animated_qrs,
)
from .wallet import HDWallet
from .coordinator import validate_coordinator_signature_if_necessary
from .config import get_config

_satoshis_per_bitcoin = Decimal(int(pow(10, 8)))

transaction_display_mode = get_config().coordinator["transaction_display"]
TOPROW = "╔═╗"
MIDDLE = "║ ║"
SECTION = "╠═╣"
SUBSECT = "╟─╢"
BOTTOM = "╚═╝"


def format_top(label, width):
    label = label.strip().upper()
    n = width - 6 - len(label)
    return (
        TOPROW[0]
        + TOPROW[1] * 2
        + " "
        + label.strip()
        + " "
        + TOPROW[1] * n
        + TOPROW[2]
    )


def format_section(label, width):
    label = label.strip().upper()
    n = width - 6 - len(label)
    return (
        SECTION[0]
        + SECTION[1] * 2
        + " "
        + label.strip()
        + " "
        + SECTION[1] * n
        + SECTION[2]
    )


def format_subsection(width):
    return SUBSECT[0] + SUBSECT[1] * (width - 2) + SUBSECT[2]


def format_bottom(width):
    return BOTTOM[0] + BOTTOM[1] * (width - 2) + BOTTOM[2]


def format_line(line, width):
    n = width - len(line) - 2
    return MIDDLE[0] + line + MIDDLE[1] * n + MIDDLE[2]


def format_bitcoin(btc):
    """Returns a 21 character string that shows the btc value with 8 places after the
    decimal aligned for amounts up to the maximum number of bitcoin.
    """
    return f"{btc:17.8f} BTC"


TX_DETAILS_WIDTH = 80


def format_tx_details(txid, version, lock_time):
    txid_line = f"TXID: {txid}"
    version_lock_line = f"Version: {version}  Lock Time: {lock_time}"
    pad = 78 - max(len(txid_line), len(version_lock_line))

    yield format_top("details", TX_DETAILS_WIDTH)
    yield format_line(" " * pad + txid_line, TX_DETAILS_WIDTH)
    yield format_line(" " * pad + version_lock_line, TX_DETAILS_WIDTH)


def format_input(index, prev_txid, prev_index, amount):
    prev = f"{prev_txid}:{prev_index}"
    idx = f"{index}:"

    yield format_line(idx + prev.rjust(78 - len(idx)), TX_DETAILS_WIDTH)
    yield format_line(" " * 11 + format_bitcoin(amount), TX_DETAILS_WIDTH)


def format_inputs(inputs):
    yield format_section("inputs", TX_DETAILS_WIDTH)
    for index, input_data in enumerate(inputs):
        yield from format_input(
            index=index + 1,
            prev_txid=input_data["prev_txhash"],
            prev_index=input_data["prev_idx"],
            amount=_sats_to_btc(input_data["sats"]),
        )
        if index + 1 < len(inputs):
            yield format_subsection(TX_DETAILS_WIDTH)


def split_string(s, n):
    """Splits s into n nearly equal length substrings."""
    d = len(s) // n
    r = len(s) % n
    lengths = [d + (i < r) for i in range(n)]
    start = 0
    result = []
    for length in lengths:
        result.append(s[start : start + length])
        start += length
    return result


def split_address(a):
    """split an address up into multiple lines, of approximately equal length, with no more than
    45 characters per line."""
    if len(a) <= 45:
        return [a]
    return split_string(a, (len(a) + 44) // 45)


def format_output(index, address, change, amount):
    parts = split_address(address)

    idx = f"{index}:"
    change_label = "CHANGE" if change else ""

    yield format_line(
        f"{idx:3} {change_label:6} {format_bitcoin(amount)} {parts[0].rjust(TX_DETAILS_WIDTH - 35)}",
        TX_DETAILS_WIDTH,
    )
    yield from (
        format_line(part.rjust(TX_DETAILS_WIDTH - 2), TX_DETAILS_WIDTH)
        for part in parts[1:]
    )


def format_outputs(outputs, top):
    if top:
        yield format_top("outputs", TX_DETAILS_WIDTH)
    else:
        yield format_section("outputs", TX_DETAILS_WIDTH)

    for index, output_data in enumerate(outputs):
        yield from format_output(
            index=index + 1,
            address=output_data["addr"],
            change=output_data["is_change"],
            amount=_sats_to_btc(output_data["sats"]),
        )
        if index + 1 < len(outputs):
            yield format_subsection(TX_DETAILS_WIDTH)


def format_totals(total_in, total_out, fee):
    yield format_section("totals", TX_DETAILS_WIDTH)
    yield format_line(f" Inputs:   {format_bitcoin(total_in)}", TX_DETAILS_WIDTH)
    yield format_line(
        f" Outputs:  {format_bitcoin(total_out)}                    Fee: {format_bitcoin(fee)}",
        TX_DETAILS_WIDTH,
    )
    yield format_bottom(TX_DETAILS_WIDTH)


def long_format_transaction(transaction_metadata):
    yield from format_tx_details(
        txid=transaction_metadata["txid"],
        version=transaction_metadata["version"],
        lock_time=transaction_metadata["locktime"],
    )
    yield from format_inputs(
        inputs=transaction_metadata["inputs_desc"],
    )
    yield from format_outputs(
        outputs=transaction_metadata["outputs_desc"],
        top=False,
    )

    input_sats = sum(inp["sats"] for inp in transaction_metadata["inputs_desc"])
    output_sats = sum(outp["sats"] for outp in transaction_metadata["outputs_desc"])

    yield from format_totals(
        total_in=_sats_to_btc(input_sats),
        total_out=_sats_to_btc(output_sats),
        fee=_sats_to_btc(input_sats - output_sats),
    )


def short_format_transaction(transaction_metadata):
    yield from format_outputs(
        outputs=transaction_metadata["outputs_desc"],
        top=True,
    )

    input_sats = sum(inp["sats"] for inp in transaction_metadata["inputs_desc"])
    output_sats = sum(outp["sats"] for outp in transaction_metadata["outputs_desc"])

    yield from format_totals(
        total_in=_sats_to_btc(input_sats),
        total_out=_sats_to_btc(output_sats),
        fee=_sats_to_btc(input_sats - output_sats),
    )


#
# ╔══ DETAILS ═══════════════════════════════════════════════════════════════════╗
# ║        TXID: 3368f33986c888d436d642a3d1f4f3fe9c837493ec6987e450579f1f7c8dcd74║
# ║        Version: 1   Lock Time: 0                                             ║
# ╠══ INPUTS ════════════════════════════════════════════════════════════════════╣
# ║1:       5e5686f54ae59105a7815e89565d4b6b41e47aca39fc3adfa2198c619dfdf748:1000║
# ║          21000000.10000000 BTC                                               ║
# ╠══ OUTPUTS ═══════════════════════════════════════════════════════════════════╣
#
# ╔══ OUTPUTS ═══════════════════════════════════════════════════════════════════╗
# ║1:               0.00100000 BTC             3KBa15krVQCe8M9LS965BuNxHojF1hbGR2║
# ╟──────────────────────────────────────────────────────────────────────────────╢
# ║2:             483.37283737 BTC  tb1asdfghjqwertyuiopqwertyuiopqwertyuiopqwert║
# ║                                 yuiopqwertyuiopqwertyuiopqwertyuiopqwertyuiop║
# ╟──────────────────────────────────────────────────────────────────────────────╢
# ║3: CHANGE        0.37283844 BTC             38LtBaM93g6wtCzGGNhrNjuV1QBx9V11Qd║
# ╠══ TOTALS ════════════════════════════════════════════════════════════════════╣
# ║ Inputs:  #####374.99988750 BTC                                               ║
# ║ Outputs: #####374.99988750 BTC       Fee: 0.00001125 BTC                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝


def _sats_to_btc(sats):
    return Decimal(sats) / _satoshis_per_bitcoin


def _format_btc(btc):
    return f"{btc} BTC"


def _format_btc_aligned(*values):
    if len(values) == 0:
        return []

    lefts = []
    rights = []
    strings = [str(value) for value in values]
    for string in strings:
        length = len(string)
        try:
            left = string.index(".")
            if left == length:
                # 'M.'
                right = 0
            elif left == 0:
                # '.N'
                right = length - 1
            else:
                # 'M.N'
                right = length - left - 1
        except ValueError:
            # M
            left = len(string)
            right = 0
        lefts.append(left)
        rights.append(right)

    max_left = max(lefts)
    max_right = max(rights)

    aligned_strings = []
    for index, string in enumerate(strings):
        length = len(string)
        left = lefts[index]
        right = rights[index]
        left_pad = (max_left - left) * " "
        right_pad = (max_right - right) * " "
        aligned_strings.append(left_pad + string + right_pad + " BTC")
    return aligned_strings


class Signer(object):
    """Signs BTC transactions.

    Accepts transactions in PSBT format read in through the camera or
    passed in on instantiation.  PSBT data must be encoded as Base64
    text.

    Performs the following validations:

    * The PSBT is syntactically valid.

    * If the transaction is spending multisig inputs:

      * all inputs must all be have the same M-of-N configuration.

      * if the transaction is creating multisig outputs in the same
        wallet, the outputs must have the same M-of-N configuration.

    * The PSBT must have an `hd_pubs` dictionary mapping XFPs to the
      BIP32 path(s) of the corresponding xpub to use when signing for
      seed identified by that XFP.

    If operating Hermit with a coordinator, the coordinator can
    additionally inject an RSA signature into the PSBT's `extra_map`
    dict (for the
    :attr:`~hermit.coordinator.COORDINATOR_SIGNATURE_KEY`).  This
    signature will be verified against an RSA public key in Hermit's
    configuration (see :attr:`~HermitConfig.DefaultCoordinator`).

    """

    def __init__(
        self,
        signing_wallet: HDWallet,
        session: PromptSession = None,
        unsigned_psbt_b64: str = None,
        testnet: bool = False,
    ) -> None:
        self.wallet = signing_wallet
        self.session = session
        self.unsigned_psbt_b64: Optional[str] = unsigned_psbt_b64
        self.testnet = testnet
        self.psbt: Optional[PSBT] = None
        self.signed_psbt_b64: Optional[str] = None

    def sign(self) -> None:
        """Initiate signing.

        Will wait for a signature request, handle validation,
        confirmation, generation, and display of a signature.
        """

        if not self.wallet.unlocked():
            # TODO: add UX flow where the user inspects the TX and can
            # then unlock the wallet?
            print_formatted_text(
                "WARNING: wallet is LOCKED; you cannot sign without first unlocking."
            )

        self.read_signature_request()
        self.parse_signature_request()
        self.validate_signature_request()

        self.generate_transaction_metadata()
        self.print_transaction_description()

        self.wallet.unlock()

        if not self.approve_signature_request():
            print_formatted_text(
                "Signature request REJECTED, aborting without attempting to sign."
            )
            return

        self.create_signature()
        self.show_signature()

    #
    # Signature Request
    #

    def read_signature_request(self):
        if self.unsigned_psbt_b64:
            # The PSBT was already passed in as an argument.
            return
        self.unsigned_psbt_b64 = read_data_from_animated_qrs()

    def parse_signature_request(self) -> None:
        print_formatted_text(HTML("Parsing PSBT..."))
        if self.unsigned_psbt_b64 is None:
            raise HermitError("No PSBT provided.")

        try:
            network = "testnet" if self.testnet else "mainnet"
            self.psbt = PSBT.parse_base64(self.unsigned_psbt_b64, network=network)
        except Exception as e:
            err_msg = "Invalid PSBT: {} ({}).".format(e, type(e).__name__)
            raise InvalidPSBT(err_msg)

    def validate_signature_request(self) -> None:
        print_formatted_text(HTML("Validating PSBT..."))
        if self.psbt is None or self.psbt.validate() is not True:
            raise InvalidPSBT("Invalid PSBT.")

        validate_coordinator_signature_if_necessary(self.psbt)

    #
    # Transaction Description
    #

    def generate_transaction_metadata(self) -> None:
        print_formatted_text(HTML("Describing signature request..."))
        self.transaction_metadata = self.psbt.describe_basic_multisig(  # type: ignore
            # xfp_for_signing=self.wallet.xfp_hex,
        )

    def print_transaction_description(self):
        if transaction_display_mode == "long":
            lines = long_format_transaction(self.transaction_metadata)
        elif transaction_display_mode == "short":
            lines = short_format_transaction(self.transaction_metadata)
        else:
            lines = self.transaction_description_lines()

        for line in lines:
            print_formatted_text(line)

    def transaction_description_lines(self) -> List[str]:
        data = self.transaction_metadata

        lines = []

        lines.extend(
            [
                "",
                f"TXID: {data['txid']}",
                f"Lock Time: {data['locktime']}",
                f"Version: {data['version']}",
                "",
                f"INPUTS ({len(data['inputs_desc'])}):",
            ]
        )

        total_input_sats = 0
        for idx, inp in enumerate(data["inputs_desc"]):
            lines.extend(
                [
                    f"  Input {idx}:",
                    f"    Prev. TXID:  {inp['prev_txhash']}",
                    f"    Prev. Index: {inp['prev_idx']}",
                    f"    Amount:      {_format_btc(_sats_to_btc(inp['sats']))}",
                    "",
                ]
            )
            total_input_sats += inp["sats"]

        lines.extend(
            [
                f"OUTPUTS ({len(data['outputs_desc'])}):",
            ]
        )

        total_output_sats = 0
        for idx, output in enumerate(data["outputs_desc"]):
            lines.extend(
                [
                    f"  Output {idx}:",
                    f"    Address: {output['addr']}",
                    f"    Amount:  {_format_btc(_sats_to_btc(output['sats']))}",
                    f"    Change?: {'Yes' if output['is_change'] else 'No'}",
                    "",
                ]
            )
            total_output_sats += output["sats"]

        total_input_btc = _sats_to_btc(total_input_sats)
        total_output_btc = _sats_to_btc(total_output_sats)
        fee_btc = _sats_to_btc(data["tx_fee_sats"])

        total_input_btc, total_output_btc, fee_btc = _format_btc_aligned(
            total_input_btc, total_output_btc, fee_btc
        )

        lines.extend(
            [
                f"Total Input Amount:  {total_input_btc}",
                f"Total Output Amount: {total_output_btc}",
                f"Fee:                 {fee_btc}",
                "",
            ]
        )

        return lines

    #
    # Signature
    #

    def approve_signature_request(self) -> bool:
        prompt_msg = "Sign the above transaction? [y/N]"

        if self.session is not None:
            response = self.session.prompt(HTML("<b>{}</b> ".format(prompt_msg)))
        else:
            response = input(prompt_msg)

        return response.strip().lower().startswith("y")

    def create_signature(self) -> None:
        """Signs a given transaction"""

        child_private_keys_to_use = []
        for xfp, bip32_paths_for_xfp in self.transaction_metadata["root_paths"].items():
            for bip32_path in bip32_paths_for_xfp:
                child_private_keys_to_use.append(
                    self.wallet.private_key(bip32_path, testnet=self.testnet)
                )

        was_signed = self.psbt is not None and self.psbt.sign_with_private_keys(
            private_keys=child_private_keys_to_use
        )
        if was_signed is False:
            raise HermitError("Failed to sign transaction")

        if self.psbt is not None:
            self.signed_psbt_b64 = self.psbt.serialize_base64()

    def show_signature(self) -> None:
        # TODO: is there a smaller signatures only format for less bandwidth?
        if self.signed_psbt_b64 is None:
            return

        print_formatted_text(HTML("<i>Signed PSBT:</i> "))
        print_formatted_text(HTML(f"{self.signed_psbt_b64}"))

        display_data_as_animated_qrs(base64_data=self.signed_psbt_b64)
