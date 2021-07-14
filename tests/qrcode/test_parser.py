import pytest
import json

import hermit
from hermit.qrcode.parser import QRParser

@pytest.fixture()
def bcur_6_part():
    with open("tests/fixtures/qrdata/bcur_6_part.json", "r") as f:
        vector = json.load(f)
    return vector

@pytest.fixture()
def bcur_single():
    with open("tests/fixtures/qrdata/bcur_single.json", "r") as f:
        vector = json.load(f)
    return vector

@pytest.fixture()
def default_qr():
    with open("tests/fixtures/qrdata/default_qr_code_data.json", "r") as f:
        vector = json.load(f)
    return vector

@pytest.fixture(params=[0,1,2])
def test_qr_set(request,bcur_6_part, bcur_single, default_qr):
    array = bcur_6_part, bcur_single, default_qr
    return array[request.param]


class TestQRParse(object):
    def test_parse_all(self, test_qr_set):
        parser = QRParser()

        assert parser.total is None
        assert parser.type is None

        for qr in test_qr_set:
            assert not parser.is_complete()
            value = parser.parse(qr)
            assert value is not None
            assert parser.type is not None
            assert parser.total is not None

        assert parser.is_complete() is True
        assert parser.decode() is not None

