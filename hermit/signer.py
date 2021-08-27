import json
from typing import Optional

from prompt_toolkit import PromptSession, print_formatted_text, HTML


from hermit.errors import HermitError, InvalidSignatureRequest
from hermit.qrcode import reader, displayer
from hermit.wallet import HDWallet

from buidl import PSBT
from buidl.bcur import BCURMulti


def describe_basic_psbt(psbt, xfp_for_signing=None):
    psbt.validate()

    tx_fee_sats = psbt.tx_obj.fee()

    root_paths_for_signing = set()

    # These will be used for all inputs and change outputs
    tx_quorum_m, tx_quorum_n = None, None

    # Gather TX info and validate
    inputs_desc = []

    for idx, psbt_in in enumerate(psbt.psbt_ins):
        if psbt_in.witness_script:
            input_quorum_m, input_quorum_n = psbt_in.witness_script.get_quorum()
        elif psbt_in.redeem_script:
            input_quorum_m, input_quorum_n = psbt_in.redeem_script.get_quorum()
        else:
            raise Exception("No witness or redeem script")

        if tx_quorum_m is None:
            tx_quorum_m = input_quorum_m
        else:
            if tx_quorum_m != input_quorum_m:
                raise Exception(
                    f"Previous input(s) set a quorum threshold of {tx_quorum_m}, but this transaction is {input_quorum_m}"
                )
        if tx_quorum_n is None:
            tx_quorum_n = input_quorum_n
        else:
            if tx_quorum_n != input_quorum_n:
                raise Exception(
                    f"Previous input(s) set a max quorum of threshold of {tx_quorum_n}, but this transaction is {input_quorum_n}"
                )

        bip32_derivs = []
        for named_pub in psbt_in.named_pubs.values():
            # Match to corresponding xpub to validate that this xpub is a participant in this input
            xfp = named_pub.root_fingerprint.hex()

            if xfp_for_signing and xfp_for_signing == xfp:
                root_paths_for_signing.add(named_pub.root_path)

            # this is very similar to what bitcoin-core's decodepsbt returns
            bip32_derivs.append(
                {
                    "pubkey": named_pub.sec().hex(),
                    "master_fingerprint": xfp,
                    "path": named_pub.root_path,
                }
            )

        # BIP67 sort order
        bip32_derivs = sorted(bip32_derivs, key=lambda k: k["pubkey"])

        input_desc = {
            "quorum": f"{tx_quorum_m}-of-{tx_quorum_n}",
            "bip32_derivs": bip32_derivs,
            "prev_txhash": psbt_in.tx_in.prev_tx.hex(),
            "prev_idx": psbt_in.tx_in.prev_index,
            "n_sequence": psbt_in.tx_in.sequence,
            "sats": psbt_in.tx_in.value(),
        }

        if psbt_in.witness_script:
            input_desc['addr'] = psbt_in.witness_script.address(network=psbt.network)
            input_desc['witness_script'] = str(psbt_in.witness_script),

        elif psbt_in.redeem_script:
            input_desc['addr'] = psbt_in.redeem_script.address(network=psbt.network)
            input_desc['redeem_script'] = str(psbt_in.redeem_script),

        inputs_desc.append(input_desc)

    total_input_sats = sum([x["sats"] for x in inputs_desc])

    # This too only supports TXs with 1-2 outputs (sweep TX OR spend+change TX):
    spend_addr, output_spend_sats = "", 0
    change_addr, output_change_sats = "", 0
    outputs_desc = []
    for idx, psbt_out in enumerate(psbt.psbt_outs):
        output_desc = {
            "sats": psbt_out.tx_out.amount,
            "addr": psbt_out.tx_out.script_pubkey.address(network=psbt.network),
            "addr_type": psbt_out.tx_out.script_pubkey.__class__.__name__.rstrip(
                "ScriptPubKey"
            ),
        }

        if psbt_out.named_pubs:
            # Confirm below that this is correct (throw error otherwise)
            output_desc["is_change"] = True

            # FIXME: Confirm this works with a change test case
            if psbt_out.witness_script:
                output_quorum_m, output_quorum_n = psbt_out.witness_script.get_quorum()
            elif psbt_out.redeem_script:
                output_quorum_m, output_quorum_n = psbt_out.redeem_script.get_quorum()

            if tx_quorum_m != output_quorum_m:
                raise Exception(
                    f"Previous output(s) set a max quorum of threshold of {tx_quorum_m}, but this transaction is {output_quorum_m}"
                )
            if tx_quorum_n != output_quorum_n:
                raise Exception(
                    f"Previous input(s) set a max cosigners of {tx_quorum_n}, but this transaction is {output_quorum_n}"
                )

            bip32_derivs = []
            for _, named_pub in psbt_out.named_pubs.items():
                # Match to corresponding xpub to validate that this xpub is a participant in this change output
                xfp = named_pub.root_fingerprint.hex()


                # this is very similar to what bitcoin-core's decodepsbt returns
                bip32_derivs.append(
                    {
                        "pubkey": named_pub.sec().hex(),
                        "master_fingerprint": xfp,
                        "path": named_pub.root_path,
                    }
                )

            # BIP67 sort order
            bip32_derivs = sorted(bip32_derivs, key=lambda k: k["pubkey"])

            change_addr = output_desc["addr"]
            output_change_sats = output_desc["sats"]

            output_desc["witness_script"] = str(psbt_out.witness_script)

        else:
            output_desc["is_change"] = False
            spend_addr = output_desc["addr"]
            output_spend_sats = output_desc["sats"]

        outputs_desc.append(output_desc)

    # Confirm if 2 outputs we only have 1 change and 1 spend (can't be 2 changes or 2 spends)
    if len(outputs_desc) == 2:
        if all(x["is_change"] for x in outputs_desc):
            raise Exception(
                f"Cannot have both outputs in 2-output transaction be change nor spend, must be 1-and-1.\n {outputs_desc}"
            )

    # comma separating satoshis for better display
    tx_summary_text = f"PSBT sends {output_spend_sats:,} sats to {spend_addr} with a fee of {tx_fee_sats:,} sats ({round(tx_fee_sats / total_input_sats * 100, 2)}% of spend)"

    to_return = {
        # TX level:
        "txid": psbt.tx_obj.id(),
        "tx_summary_text": tx_summary_text,
        "locktime": psbt.tx_obj.locktime,
        "version": psbt.tx_obj.version,
        "network": psbt.network,
        "tx_fee_sats": tx_fee_sats,
        "total_input_sats": total_input_sats,
        "output_spend_sats": output_spend_sats,
        "change_addr": change_addr,
        "output_change_sats": output_change_sats,
        "change_sats": total_input_sats - tx_fee_sats - output_spend_sats,
        "spend_addr": spend_addr,
        # Input/output level
        "inputs_desc": inputs_desc,
        "outputs_desc": outputs_desc,
    }

    if xfp_for_signing:
        if not root_paths_for_signing:
            # We confirmed above that all inputs have identical encumberance so we choose the first one as representative
            err = [
                "Did you enter a root fingerprint for another seed?",
                f"The xfp supplied ({xfp_for_signing}) does not correspond to the transaction inputs, which are {input_quorum_m} of the following:",
                ", ".join(sorted(list(hdpubkey_map.keys()))),
            ]
            raise Exception("\n".join(err))

        to_return["root_paths"] = root_paths_for_signing

    return to_return

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

        self.display_request()

        if not self.wallet.unlocked():
            print_formatted_text(
                "Wallet is LOCKED, aborting without attempting to sign"
            )
            return

        if self._confirm_create_signature():
            self.create_signature()
            self._show_signature()

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
            for idx, inp in enumerate(tx_desc["inputs_desc"]):
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
            for idx, output in enumerate(tx_desc["outputs_desc"]):
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

    def _show_signature(self) -> None:
        # TODO: is there a smaller signatures only format for less bandwidth?
        print_formatted_text(HTML("<i>SIGNED PSBT:</i> "))
        print_formatted_text(HTML(f"{self.signed_psbt_b64}"))

        displayer.display_qr_code(self.signed_psbt_b64)
