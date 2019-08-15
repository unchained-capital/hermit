import pytest
import base64
import lzma

import hermit

_DECODED = 'foobar'
_ENCODED = b'LUAABAAA7777777777776ABTDPWMIYSCAQSV77773C4QAAA='

@pytest.mark.qrcode
class TestDecodeQRCodeData(object):

    def test_valid_format(self):
        assert _DECODED == hermit.decode_qr_code_data(_ENCODED)

    def test_empty_bytes(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(b'')

    def test_improper_base32(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(_ENCODED[:-1])

    def test_base64(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(base64.b64encode(lzma.compress(_DECODED.encode('utf-8'))))

    def test_uncompressed(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(base64.b32encode(_DECODED.encode('utf-8')))

    def test_not_utf8(self):
        with pytest.raises(hermit.InvalidSignatureRequest):
            hermit.decode_qr_code_data(base64.b32encode(lzma.compress(_DECODED.encode('utf-16'))))

@pytest.mark.qrcode
class TestEncodeQRCodeData(object):

    def test_simple_decoded_data(self):
        assert _ENCODED == hermit.encode_qr_code_data(_DECODED)
