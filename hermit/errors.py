class HermitError(Exception):
    """Generic Hermit Error"""
    pass


class InvalidSignatureRequest(HermitError):
    """Signature request was not valid"""

    def __init__(self, message: str) -> None:
        """Initialize a new `InvalidSignatureRequest`

        :param message: more details on the error.
        """

        HermitError.__init__(self,
                             "Invalid signature request: {}.".format(message))
