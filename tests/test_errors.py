import pytest

from hermit.errors import HermitError, InvalidSignatureRequest


class TestHermitErrors(object):
    def test_HermitError_raisable(self):
        with pytest.raises(HermitError):
            raise HermitError

    def test_InvalidSignatureRequest_raisable_with_message(self):
        with pytest.raises(InvalidSignatureRequest) as e_info:
            raise InvalidSignatureRequest("test")
        assert str(e_info.value) == "Invalid signature request: test."
