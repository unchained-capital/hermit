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

        if not self.wallet.unlocked():
            print_formatted_text(
                "Wallet is LOCKED, aborting without attempting to sign."
            )
            return

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
            self.psbt = PSBT.parse_base64(
                self.unsigned_psbt_b64,
            )
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
        self.transaction_metadata = self.psbt.describe_basic_multisig(
            # xfp_for_signing=self.wallet.xfp_hex,
        )

    def print_transaction_description(self):
        for line in self.transaction_description_lines():
            print_formatted_text(line)

    def transaction_description_lines(self) -> List[str]:
        data = self.transaction_metadata

        lines = [
            f"{data['tx_summary_text']}",
        ]

        lines.extend(
            [
                "",
                f"TXID: {data['txid']}",
                f"Fee in Sats: {data['tx_fee_sats']:,}",
                f"Lock Time: {data['locktime']}",
                f"Version: {data['version']}",
                "",
                "INPUTS:",
            ]
        )

        for idx, inp in enumerate(data["inputs_desc"]):
            lines.extend(
                [
                    f"  Input {idx}:",
                    f"    Previous TX Hash: {inp['prev_txhash']}",
                    f"    Previous Output Index: {inp['prev_idx']}",
                    f"    Sats: {inp['sats']:,}",
                    # f"    bip32: {inp['bip32_derivs']}",
                    "",
                ]
            )

            # TODO: more input stuff here
        lines.append("OUTPUTS:")
        for idx, output in enumerate(data["outputs_desc"]):
            lines.extend(
                [
                    f"  Output {idx}:",
                    f"    Address: {output['addr']}",
                    f"    Sats: {output['sats']:,}",
                    # f"    bip32: {output['bip32_derivs']}",
                    f"    Is Change?: {output['is_change']}",
                    "",
                ]
            )
            # TODO: more output stuff here
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

        display_data_as_animated_qrs(self.signed_psbt_b64)
