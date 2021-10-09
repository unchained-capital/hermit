class HermitError(Exception):
    """Base class for all Hermit errors."""
    pass

class InvalidQRCodeSequence(HermitError):
    """Base class for all exceptions in parsing a QR code sequence."""
    pass


class InvalidPSBT(HermitError):
    """Raised to indicate a PSBT was invalid."""
    pass

class InvalidSignatureRequest(HermitError):
    """Raised to indicate a signature request was invalid."""
    pass

class InvalidCoordinatorSignature(HermitError):
    """Raised to indicate a signature from a coordinator was invalid."""
    pass
