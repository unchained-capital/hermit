import json
import re
from typing import Optional, Dict

from prompt_toolkit import PromptSession

import hermit
from hermit.errors import HermitError, InvalidSignatureRequest
from hermit.qrcode import reader, displayer
from hermit.wallet import (compressed_private_key_from_bip32,
                           compressed_public_key_from_bip32, HDWallet)


class Signer(object):
    """Abstract class from which to subclass signing classes for specific assets.

    This class implements the basic framework required to receive a
    signature request and return a signature.

    Subclasses should implement the following API methods:

    * ``validate_request``
    * ``display_request``
    * ``create_signature``

    """

    def __init__(self,
                 signing_wallet: HDWallet,
                 session: PromptSession = None) -> None:
        self.wallet = signing_wallet
        self.session = session
        self.signature: Optional[Dict] = None
        self.request_data: Optional[str] = None

    def sign(self, testnet: bool = False) -> None:
        """Initiate signing.

        Will wait for a signature request, handle validation,
        confirmation, generation, and display of a signature.
        """

        self.testnet = testnet
        self._wait_for_request()
        if self.request_data:
            self._parse_request()
            self._validate_request()
            if self._confirm_create_signature():
                self._generate_child_keys()
                self.create_signature()
                self._show_signature()

    def validate_request(self) -> None:
        """Validate a signature request.

        Concrete subclasses should override this method.

        The contents of the signature request will already be parsed
        from QR code and available as ``self.request``.

        Invalid requests should raise an appropriate error class with
        message.

        The presence in the request of a valid path to a BIP32 node to
        use when signing is already validated.

        """
        pass

    def display_request(self) -> None:
        """Display a signature request.

        Concrete subclasses should override this method.

        The contents of the signature request will already be parsed
        from QR code and available as ``self.request``.

        Use ``print`` to display the signature in a way that readable on
        consoles.

        """
        pass

    def create_signature(self) -> None:
        """Create a signature.

        Concrete subclasses should override this method.

        The contents of the signature request will already be parsed
        from QR code and available as ``self.request``.

        The signature data should be saved as ``self.signature``.

        """
        pass

    def _wait_for_request(self) -> None:
        self.request_data = reader.read_qr_code()

    def _parse_request(self) -> None:
        if self.request_data is not None:
            try:
                self.request = json.loads(self.request_data)
            except ValueError as e:
                err_msg = ("Invalid signature request: {} ({})"
                           .format(e, type(e).__name__))
                raise HermitError(err_msg)
        else:
            raise HermitError('No Request Data')

    def _validate_request(self) -> None:
        self._validate_bip32_path()
        self.validate_request()

    def _validate_bip32_path(self) -> None:
        bip32_path_regex = "^m(/[0-9]+'?)+$"
        if 'bip32_path' not in self.request:
            raise InvalidSignatureRequest("no BIP32 path")
        self.bip32_path = self.request['bip32_path']
        if not isinstance(self.bip32_path, (str,)):
            raise InvalidSignatureRequest("BIP32 path must be a string")
        if not re.match(bip32_path_regex, self.bip32_path):
            err_msg = "invalid BIP32 path formatting"
            raise InvalidSignatureRequest(err_msg)
        nodes = self.bip32_path.split('/')[1:]
        node_values = [int(x.replace("'", "")) for x in nodes]
        for node_value in node_values:
            if node_value > 2147483647:
                err_msg = "invalid BIP32 path"
                raise InvalidSignatureRequest(err_msg)

    def _confirm_create_signature(self) -> bool:
        self.display_request()
        prompt_msg = "Sign the above transaction? [y/N] "

        if self.session is not None:
            response = self.session.prompt(prompt_msg)
        else:
            response = input(prompt_msg)

        return response.strip().lower().startswith('y')


    def _show_signature(self) -> None:
        name = self._signature_label()
        print("Signature Data: ")
        print(json.dumps(self.signature, indent=2))
        displayer.display_qr_code(self._serialized_signature(), name=name)

    def _serialized_signature(self) -> str:
        return json.dumps(self.signature)

    def _generate_child_keys(self) -> None:
        self.xprv = self.wallet.extended_private_key(self.bip32_path)
        self.xpub = self.wallet.extended_public_key(self.bip32_path)
        self.private_key = compressed_private_key_from_bip32(self.xprv).hex()
        self.public_key = compressed_public_key_from_bip32(self.xpub).hex()

    def _signature_label(self) -> str:
        return 'Signature'
