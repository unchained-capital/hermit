import pytest
import base64
import gzip

import hermit

_DECODED = "foobar"
_ENCODED = b"D6FQQACPVZOV2AX7JPF46T2KFQBABFI762PAMAAAAA======"


@pytest.mark.qrcode
class TestDecodeQRCodeData(object):
    def test_valid_format(self):
        assert _DECODED == hermit.decode_qr_code_data(_ENCODED)

    def test_empty_bytes(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(b"")

    def test_improper_base32(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(_ENCODED[:-1])

    def test_base64(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(
                base64.b64encode(gzip.compress(_DECODED.encode("utf-8")))
            )

    def test_uncompressed(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(base64.b32encode(_DECODED.encode("utf-8")))

    def test_not_utf8(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(
                base64.b32encode(gzip.compress(_DECODED.encode("utf-16")))
            )


@pytest.mark.qrcode
class TestEncodeQRCodeData(object):
    def test_recoverability(self):
        assert _DECODED == hermit.decode_qr_code_data(
            hermit.encode_qr_code_data(_DECODED)
        )

    def test_empty_string(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.encode_qr_code_data("")

    def test_bytes(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.encode_qr_code_data(_DECODED.encode("utf-8"))
