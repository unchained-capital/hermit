import base64
import gzip
import random
import string

from numpy import array
import cv2
import pytest
import qrcode


#
# Version 40 QRcode Storage Limits with Low Error Correction
# Mixed Bytes: 23,648 (tests show this library is limited to 23,549)
# Numeric: 7,089
# Alphanumeric: 4,296
# Binary: 2,953
#


@pytest.mark.qrcode
class TestQRCodeStorage(object):
    def test_numeric_maximum(self):
        N = 7089
        data = "".join([random.choice(string.digits) for _ in range(N)])
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make()
        assert True

    def test_numeric_overflow(self):
        N = 7090
        data = "".join([random.choice(string.digits) for _ in range(N)])
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        with pytest.raises(qrcode.exceptions.DataOverflowError):
            qr.make()
        assert True

    def test_alphanumeric_maximum(self):
        N = 4296
        data = "".join(
            [random.choice(string.digits + string.ascii_uppercase) for _ in range(N)]
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make()
        assert True

    def test_alphanumeric_overflow(self):
        N = 4297
        data = "".join(
            [random.choice(string.digits + string.ascii_uppercase) for _ in range(N)]
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data, optimize=0)
        with pytest.raises(qrcode.exceptions.DataOverflowError):
            qr.make()
        assert True

    def test_binary_maximum(self):
        N = 2953
        data = bytes(bytearray((random.getrandbits(8) for i in range(N))))
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make()
        assert True

    def test_binary_overflow(self):
        N = 2954
        data = bytes(bytearray((random.getrandbits(8) for i in range(N))))
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data, optimize=0)
        with pytest.raises(qrcode.exceptions.DataOverflowError):
            qr.make()
        assert True

    def test_bits_maximum(self):
        N = 23549
        data = 1 << N
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make()
        assert True

    def test_bits_overflow(self):
        N = 23550
        data = 1 << N
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        with pytest.raises(qrcode.exceptions.DataOverflowError):
            qr.make()
        assert True

    def test_alphanumeric_compression_maximum(self):
        M = 4
        N = 2000
        data = "".join(
            [random.choice(string.digits + string.ascii_letters) * M for _ in range(N)]
        )
        data = data.encode("utf-8")
        print(len(data))  # 10000
        data = gzip.compress(data)
        data = base64.b32encode(data)

        print(len(data))
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make()
        assert len(data) < 4296
        assert True
