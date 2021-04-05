import json
from typing import Optional

from prompt_toolkit import PromptSession, print_formatted_text, HTML


from hermit.errors import HermitError, InvalidSignatureRequest
from hermit.qrcode import reader, displayer
from hermit.wallet import HDWallet

from buidl import PSBT


class BitcoinSigner(object):

    """Signs BTC transactions

    Takes a valid PSBT.
    """

    def __init__(
        self,
        signing_wallet: HDWallet,
        session: PromptSession = None,
        unsigned_psbt_b64: str = None,
    ) -> None:
        self.wallet = signing_wallet
        self.session = session
        self.unsigned_psbt_b64: Optional[str] = unsigned_psbt_b64

    def sign(self, testnet: bool = False) -> None:
        """Initiate signing.

        Will wait for a signature request, handle validation,
        confirmation, generation, and display of a signature.
        """
        if not self.wallet.unlocked():
            # TODO: add UX flow where the user inspects the TX and can then unlock the wallet?
            print_formatted_text("WARNING: wallet is LOCKED.")
            print_formatted_text("You can inspect an unsigned PSBT, but you cannot sign it without first unlocking the wallet.")

        self.testnet = testnet
        if not self.unsigned_psbt_b64:
            # Get unsigned PSBT from webcam (QR gif) if not already passed in as an argument
            self.unsigned_psbt_b64 = reader.read_qr_code()

        self.parse_psbt()
        self.validate_psbt()
        self.display_request()
        if not self.wallet.unlocked():
            print_formatted_text("Wallet is LOCKED, aborting without attempting to sign")
            return

        if self._confirm_create_signature():
            self.create_signature()
            self._show_signature()

    def parse_psbt(self) -> None:
        if self.unsigned_psbt_b64 is None:
            raise HermitError("No PSBT Supplied")

        try:
            self.psbt_obj = PSBT.parse_base64(
                self.unsigned_psbt_b64, testnet=self.testnet
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

        self.tx_description = self.psbt_obj.describe_basic_multisig_tx(
            root_fingerprint_for_signing=self.wallet.xfp_hex
        )

    def display_request(self, verbose=False) -> None:
        """Displays the transaction to be signed"""
        tx_desc = self.tx_description

        print_formatted_text(HTML(f"{tx_desc['tx_summary_text']}"))

        if (
            verbose or True
        ):  # TODO: set this toggle somewhere and make this a nice display with complete info
            print_formatted_text(HTML(""))
            print_formatted_text(HTML(f"<i>TX ID:</i> {tx_desc['txid']}"))
            print_formatted_text(
                HTML(f"<i>Fee in Sats:</i> {tx_desc['tx_fee_sats']:,}")
            )
            print_formatted_text(HTML(f"<i>Lock Time:</i> {tx_desc['locktime']}"))
            print_formatted_text(HTML(f"<i>Version:</i> {tx_desc['version']}"))
            print_formatted_text(HTML(""))
            print_formatted_text(HTML("<i>INPUTS:</i>"))
            for cnt, inp in enumerate(tx_desc["inputs_desc"]):
                print_formatted_text(HTML(f"\t<i>Input #:</i> {cnt}"))
                print_formatted_text(
                    HTML(f"\t\t<i>Previous TX Hash:</i> {inp['prev_txhash']}")
                )
                print_formatted_text(
                    HTML(f"\t\t<i>Previous Output Index:</i> {inp['prev_idx']}")
                )
                print_formatted_text(HTML(f"\t\t<i>Sats:</i> {inp['sats']:,}"))
                # TODO: more input stuff here
            print_formatted_text(HTML("<i>OUTPUTS:</i>"))
            for cnt, output in enumerate(tx_desc["outputs_desc"]):
                print_formatted_text(HTML(f"\t<i>Output #:</i> {cnt}"))
                print_formatted_text(HTML(f"\t\t<i>Address:</i> {output['addr']}"))
                print_formatted_text(HTML(f"\t\t<i>Sats:</i> {output['sats']:,}"))
                print_formatted_text(
                    HTML(f"\t\t<i>Is Change?:</i> {output['is_change']}")
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

    def _show_signature(self) -> None:
        # TODO: is there a smaller signatures only format for less bandwidth?
        print_formatted_text(HTML("<i>SIGNED PSBT:</i> "))
        print_formatted_text(HTML(f"{self.signed_psbt_b64}"))
        displayer.display_qr_code(
            json.dumps({"psbt": self.signed_psbt_b64}), name="Signed PSBT"
        )
