from hermit.qrcode import displayer
from hermit.signer.base import Signer


class EchoSigner(Signer):
    """Returns the signature request data as a signature.

    This class is useful for debugging signature requests.
    """

    #
    # Validation
    #

    def validate_request(self) -> None:
        """Validate the signature request
        
        Does nothing :)
        """
        pass

    #
    # Display
    #

    def display_request(self) -> None:
        """Prints the signature request"""
        print("""QR Code:
        {}
        """.format(self.request))

    def create_signature(self) -> None:
        """Create a fake signature

        The signature data is just the request data.
        """
        self.signature = self.request

    def _signature_label(self) -> str:
        return 'Request'
