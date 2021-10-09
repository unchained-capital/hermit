class HermitError(Exception):
    """Base class for all Hermit errors."""
    pass

class InvalidQRCodeSequence(HermitError):
    """Base class for all exceptions in parsing a QR code sequence."""
    pass


class InvalidSignatureRequest(HermitError):
    """Raised to indicate a signature request PSBT was invalid."""
    pass

