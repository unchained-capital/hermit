import json
from typing import Optional

from prompt_toolkit import PromptSession, print_formatted_text, HTML


from hermit.errors import HermitError, InvalidSignatureRequest
from hermit.qrcode import reader, displayer
from hermit.wallet import HDWallet

from .confirm_transaction import confirm_transaction_dialog

from buidl import PSBT
from buidl.bcur import BCURMulti

from .psbt import describe_basic_psbt

class BitcoinSigner(object):

    """Signs BTC transactions

    Takes a valid PSBT.
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

    def sign(self) -> None:
        """Initiate signing.

        Will wait for a signature request, handle validation,
        confirmation, generation, and display of a signature.
        """
        if not self.wallet.unlocked():
            # TODO: add UX flow where the user inspects the TX and can then unlock the wallet?
            print_formatted_text("WARNING: wallet is LOCKED.")
            print_formatted_text(
                "You can inspect an unsigned PSBT, but you cannot sign it without first unlocking the wallet."
            )

        if not self.unsigned_psbt_b64:
            # Get unsigned PSBT from webcam (QR gif) if not already passed in as an argument
            self.unsigned_psbt_b64 = reader.read_qr_code()

        self.parse_psbt()
        self.validate_psbt()

        if not self.wallet.unlocked():
            self.print_transaction_description()
            print_formatted_text(
                "Wallet is LOCKED, aborting without attempting to sign"
            )
            return

        sign = confirm_transaction_dialog(transaction=self.transaction_description()).run()

        if not sign:
            print_formatted_text(
                "Signature request REJECTED, aborting without attempting to sign"
            )
            return

        self.create_signature()
        self.show_signature()

    def parse_psbt(self) -> None:
        if self.unsigned_psbt_b64 is None:
            raise HermitError("No PSBT Supplied")

        try:
            self.psbt_obj = PSBT.parse_base64(
                self.unsigned_psbt_b64,
            )
        except Exception as e:
            err_msg = "Invalid PSBT: {} ({})".format(e, type(e).__name__)
            raise HermitError(err_msg)


    def _confirm_create_signature(self) -> bool:
        prompt_msg = "Sign the above transaction? [y/N] "

        if self.session is not None:
            response = self.session.prompt(HTML("<b>{}</b>".format(prompt_msg)))
        else:
            response = input(prompt_msg)

        return response.strip().lower().startswith("y")

    def validate_psbt(self) -> None:
        if self.psbt_obj.validate() is not True:
            raise InvalidSignatureRequest("Invalid PSBT")

        self.tx_description = describe_basic_psbt(
            self.psbt_obj,
            xfp_for_signing=self.wallet.xfp_hex,
        )

    def transaction_description(self, verbose=True) -> str:
        return "\n".join(map(lambda line: line, self._transaction_description_lines(verbose=verbose)))

    def print_transaction_description(self, verbose=True):
        for line in self._transaction_description_lines(verbose=verbose):
            print_formatted_text(line)

    def _transaction_description_lines(self, verbose=True) -> [str]:
        tx_desc = self.tx_description

        lines = [
            f"{tx_desc['tx_summary_text']}",
        ]

        if verbose:
        # TODO: set this toggle somewhere and make this a nice display with complete info

            lines.extend([
                "",
                f"TXID: {tx_desc['txid']}",
                f"Fee in Sats: {tx_desc['tx_fee_sats']:,}",
                f"Lock Time: {tx_desc['locktime']}",
                f"Version: {tx_desc['version']}",
                "",
                "INPUTS:",
            ])

            for idx, inp in enumerate(tx_desc["inputs_desc"]["inputs_desc"]):
                lines.extend([
                    f"  Input {idx}:",
                    f"    Previous TX Hash: {inp['prev_txhash']}",
                    f"    Previous Output Index: {inp['prev_idx']}",
                    f"    Sats: {inp['sats']:,}",
                    #f"    bip32: {inp['bip32_derivs']}",
                    "",
                ])

                # TODO: more input stuff here
            lines.append("OUTPUTS:")
            for idx, output in enumerate(tx_desc["outputs_desc"]["outputs_desc"]):
                lines.extend([
                    f"  Output {idx}:",
                    f"    Address: {output['addr']}",
                    f"    Sats: {output['sats']:,}",
                    #f"    bip32: {output['bip32_derivs']}",
                    f"    Is Change?: {output['is_change']}",
                    "",
                ])
                # TODO: more output stuff here
        return lines

    def display_request(self, verbose=False) -> None:
        """Displays the transaction to be signed"""
        tx_desc = self.tx_description

        print_formatted_text(HTML(f"{tx_desc['tx_summary_text']}"))

        if (
            verbose or True
        ):  # TODO: set this toggle somewhere and make this a nice display with complete info
            print_formatted_text(HTML(""))
            print_formatted_text(HTML(f"<i>TXID:</i> {tx_desc['txid']}"))
            print_formatted_text(
                HTML(f"<i>Fee in Sats:</i> {tx_desc['tx_fee_sats']:,}")
            )
            print_formatted_text(HTML(f"<i>Lock Time:</i> {tx_desc['locktime']}"))
            print_formatted_text(HTML(f"<i>Version:</i> {tx_desc['version']}"))
            print_formatted_text(HTML(""))
            print_formatted_text(HTML("<i>INPUTS:</i>"))
            for idx, inp in enumerate(tx_desc["inputs_desc"]["inputs_desc"]):
                print_formatted_text(HTML(f"  <i>Input {idx}:</i>"))
                print_formatted_text(
                    HTML(f"    <i>Previous TX Hash:</i> {inp['prev_txhash']}")
                )
                print_formatted_text(
                    HTML(f"    <i>Previous Output Index:</i> {inp['prev_idx']}")
                )
                print_formatted_text(HTML(f"    <i>Sats:</i> {inp['sats']:,}"))
                # TODO: more input stuff here
            print_formatted_text(HTML("<i>OUTPUTS:</i>"))
            for idx, output in enumerate(tx_desc["outputs_desc"]["outputs_desc"]):
                print_formatted_text(HTML(f"  <i>Output {idx}:</i>"))
                print_formatted_text(HTML(f"    <i>Address:</i> {output['addr']}"))
                print_formatted_text(HTML(f"    <i>Sats:</i> {output['sats']:,}"))
                print_formatted_text(
                    HTML(f"    <i>Is Change?:</i> {output['is_change']}")
                )
                # TODO: more output stuff here

    def create_signature(self) -> None:
        """Signs a given transaction"""

        child_private_keys_to_use = self.wallet.get_child_private_key_objs(
            bip32_paths=self.tx_description["root_paths"]
        )

        was_signed = self.psbt_obj.sign_with_private_keys(
            private_keys=child_private_keys_to_use
        )
        if was_signed is False:
            raise HermitError("Failed to Sign Transaction")

        self.signed_psbt_b64 = self.psbt_obj.serialize_base64()
        print_formatted_text("success")

    def show_signature(self) -> None:
        # TODO: is there a smaller signatures only format for less bandwidth?
        print_formatted_text(HTML("<i>SIGNED PSBT:</i> "))
        print_formatted_text(HTML(f"{self.signed_psbt_b64}"))

        displayer.display_qr_code(self.signed_psbt_b64)
