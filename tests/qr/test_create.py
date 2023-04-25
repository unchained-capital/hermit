from base64 import b64encode
from unittest.mock import Mock
from pytest import raises

from qrcode import QRCode

from hermit import qr_to_image, create_qr_sequence, HermitError
from hermit.qr import create_qr


class TestCreateQRSequence(object):
    def setup(self):
        self.data = open("tests/fixtures/lorem_ipsum.txt", "r").read()
        self.base64_data = b64encode(self.data.encode("utf8")).decode("utf8")

    def test_with_no_arguments(self):
        with raises(HermitError) as e:
            create_qr_sequence()
        assert "Must provide" in str(e)

    def test_with_data(self):
        sequence = create_qr_sequence(data=self.data)
        assert len(sequence) == 10
        for qr in sequence:
            assert isinstance(qr, QRCode)

    def test_with_base64_data(self):
        sequence = create_qr_sequence(base64_data=self.base64_data)
        assert len(sequence) == 10
        for qr in sequence:
            assert isinstance(qr, QRCode)

    def test_with_both(self):
        sequence = create_qr_sequence(data=self.data, base64_data=self.base64_data)
        assert len(sequence) == 10
        for qr in sequence:
            assert isinstance(qr, QRCode)


def test_qr_to_image():
    qr = Mock()
    mock_make_image = Mock()
    qr.make_image = mock_make_image
    mock_image = Mock()
    mock_make_image.return_value = mock_image
    assert qr_to_image(qr) == mock_image
    mock_make_image.assert_called_once_with(fill_color="black", back_color="white")


def test_create_qr():
    data = "data"
    qr = create_qr(data)
    assert isinstance(qr, QRCode)
