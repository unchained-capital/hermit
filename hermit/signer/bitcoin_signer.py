import binascii
from collections import defaultdict
from hashlib import sha256
from typing import Dict

from bitcoin import SelectParams
from bitcoin import base58
from bitcoin.core import COutPoint, CMutableTxOut, CMutableTxIn, CTransaction
from bitcoin.core.script import SignatureHash, SIGHASH_ALL, CScript
from bitcoin.wallet import (CBitcoinAddress,
                            CBitcoinAddressError,
                            P2SHBitcoinAddress)
import bitcoin
import ecdsa

from hermit.errors import InvalidSignatureRequest
from hermit.signer.base import Signer


def generate_multisig_address(redeemscript: str, testnet: bool = False) -> str:
    """
    Generates a P2SH-multisig Bitcoin address from a redeem script

    Args:
        redeemscript: hex-encoded redeem script
                      use generate_multisig_redeem_script to create
                      the redeem script from three compressed public keys
         testnet: Should the address be testnet or mainnet?

    Example:
        TODO
    """

    if testnet:
        bitcoin.SelectParams('testnet')

    redeem_script = CScript(bitcoin.core.x(redeemscript))

    addr = P2SHBitcoinAddress.from_redeemScript(redeem_script)

    return str(addr)


class BitcoinSigner(Signer):
    """Signs BTC transactions"""
    

    #
    # Validation
    #

    def validate_request(self) -> None:
        """Validates a signature request

        Validates

        * the redeem script
        * inputs & outputs
        * fee
        """
        if self.testnet:
            SelectParams('testnet')
        else:
            SelectParams('mainnet')
        self._validate_redeem_script()
        self._validate_inputs()
        self._validate_outputs()
        self._validate_fee()

    def _validate_redeem_script(self) -> None:
        if 'redeem_script' not in self.request:
            raise InvalidSignatureRequest("no redeem script")
        try:
            binascii.unhexlify(self.request['redeem_script'].encode('utf8'))
        except ValueError:
            raise InvalidSignatureRequest("redeem script is not valid hex")
        self.redeem_script = self.request['redeem_script']
        self.address = generate_multisig_address(self.redeem_script,
                                                 self.testnet)

    def _validate_inputs(self) -> None:
        if 'inputs' not in self.request:
            raise InvalidSignatureRequest("no inputs")
        self.inputs = self.request['inputs']
        if not isinstance(self.inputs, list):
            raise InvalidSignatureRequest("inputs is not an array")
        if len(self.inputs) == 0:
            raise InvalidSignatureRequest("at least one input is required")
        for input in self.inputs:
            self._validate_input(input)

    def _validate_input(self, input: Dict) -> None:
        if 'amount' not in input:
            raise InvalidSignatureRequest("no amount in input")
        if type(input['amount']) != int:
            err_msg = "input amount must be an integer (satoshis)"
            raise InvalidSignatureRequest(err_msg)
        if input['amount'] <= 0:
            raise InvalidSignatureRequest("invalid input amount")

        if 'txid' not in input:
            raise InvalidSignatureRequest("no txid in input")
        if len(input['txid']) != 64:
            raise InvalidSignatureRequest("txid must be 64 characters")
        try:
            binascii.unhexlify(input['txid'].encode('utf8'))
        except ValueError:
            err_msg = "input TXIDs must be hexadecimal strings"
            raise InvalidSignatureRequest(err_msg)

        if 'index' not in input:
            raise InvalidSignatureRequest("no index in input")
        if type(input['index']) != int:
            err_msg = "input index must be an integer"
            raise InvalidSignatureRequest(err_msg)
        if input['index'] < 0:
            raise InvalidSignatureRequest("invalid input index")

    def _validate_outputs(self) -> None:
        if 'outputs' not in self.request:
            raise InvalidSignatureRequest("no outputs")
        self.outputs = self.request['outputs']
        if not isinstance(self.outputs, list):
            raise InvalidSignatureRequest("outputs is not an array")
        if len(self.outputs) == 0:
            raise InvalidSignatureRequest("at least one output is required")
        for output in self.outputs:
            self._validate_output(output)

    def _validate_output(self, output: Dict) -> None:
        if 'address' not in output:
            raise InvalidSignatureRequest("no address in output")
        if not isinstance(output['address'], (str,)):
            err_msg = "output addresses must be base58-encoded strings"
            raise InvalidSignatureRequest(err_msg)

        if output['address'][:2] in ('bc', 'tb'):
            err_msg = "bech32 addresses are unsupported (output)"
            raise InvalidSignatureRequest(err_msg)
        try:
            base58.CBase58Data(output['address'])
        except base58.InvalidBase58Error:
            err_msg = "output addresses must be base58-encoded strings"
            raise InvalidSignatureRequest(err_msg)
        except base58.Base58ChecksumError:
            err_msg = "invalid output address checksum"
            raise InvalidSignatureRequest(err_msg)
        try:
            CBitcoinAddress(output['address'])
        except CBitcoinAddressError:
            err_msg = "invalid output address (check mainnet vs. testnet)"
            raise InvalidSignatureRequest(err_msg)

        if 'amount' not in output:
            raise InvalidSignatureRequest("no amount in output")
        if type(output['amount']) != int:
            err_msg = "output amount must be an integer (satoshis)"
            raise InvalidSignatureRequest(err_msg)
        if output['amount'] <= 0:
            raise InvalidSignatureRequest("invalid output amount")

    def _validate_fee(self) -> None:
        sum_inputs = sum([input['amount'] for input in self.inputs])
        sum_outputs = sum([output['amount'] for output in self.outputs])
        self.fee = sum_inputs - sum_outputs
        if self.fee < 0:
            raise InvalidSignatureRequest("fee cannot be negative")

    #
    # Display
    #

    def display_request(self) -> None:
        """Displays the transaction to be signed"""
        print("""ADDRESS:
{}

INPUTS:
{}

OUTPUTS:
{}

FEE: {} BTC

SIGNING AS: {}
""".format(self.address,
           self._formatted_inputs(),
           self._formatted_outputs(),
           self._format_amount(self.fee),
           self.bip32_path))

    # We currently only support a single address for all inputs
    def _formatted_inputs(self) -> str:
        addresses: Dict = defaultdict(int)
        for input in self.inputs:
            addresses[self.address] += input['amount']
        lines = []
        for address in addresses:
            lines.append("  ADDRESS {}\tAMOUNT {} BTC".format(
                address,
                self._format_amount(addresses[address])))
        return "\n".join(lines)

    def _formatted_outputs(self) -> str:
        formatted_outputs = [self._format_output(output)
                             for output
                             in self.outputs]
        return "\n".join(formatted_outputs)

    def _format_output(self, output: Dict) -> str:
        return "  ADDRESS {}\tAMOUNT {} BTC".format(
            output['address'],
            self._format_amount(output['amount']))

    def _format_amount(self, amount) -> str:
        return "%0.8f" % (amount / pow(10, 8))

    #
    # Signing
    #

    def create_signature(self) -> None:
        """Signs a given transaction"""
        # Keys are derived in base.py

        if self.testnet:
            SelectParams('testnet')
        else:
            SelectParams('mainnet')

        # Parse Redeemscript
        redeem_script = CScript(bitcoin.core.x(self.redeem_script))

        # Construct Inputs
        tx_inputs = []
        for input in self.inputs:
            txid = bitcoin.core.lx(input['txid'])
            vout = input['index']
            tx_inputs.append(CMutableTxIn(COutPoint(txid, vout)))

        # Construct Outputs
        tx_outputs = []

        for output in self.outputs:
            output_script = (CBitcoinAddress(output['address'])
                             .to_scriptPubKey())
            tx_outputs.append(CMutableTxOut(output['amount'], output_script))

        # Create Transaction
        tx = CTransaction(tx_inputs, tx_outputs)

        # Create Signature Hashes
        signature_hashes = [SignatureHash(redeem_script, tx, ii, SIGHASH_ALL)
                            for ii
                            in range(len(tx_inputs))]

        # Create SigningKey
        signingkey = ecdsa.SigningKey.from_string(
            bytes.fromhex(self.private_key),
            curve=ecdsa.SECP256k1)

        # Sign
        # WARNING: We do not append the SIGHASH_ALL byte,
        # transaction constructioin should account for that.
        signatures = []
        for sighash in signature_hashes:
            signatures.append(
                signingkey.sign_digest_deterministic(
                    sighash,
                    sha256,
                    sigencode=ecdsa.util.sigencode_der_canonize
                ).hex()
            )

        # Assign result
        result = {"pubkey": self.public_key,
                  "signatures": signatures}

        self.signature = result
