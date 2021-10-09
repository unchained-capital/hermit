import pytest
import json

from hermit.qr import GenericReassembler

@pytest.fixture()
def bcur_multi():
    with open("tests/fixtures/qrdata/bcur_6_part.json", "r") as f:
        vector = json.load(f)
    return vector

@pytest.fixture()
def bcur_singles():
    with open("tests/fixtures/qrdata/bcur_single.json", "r") as f:
        vector = json.load(f)
    return vector

@pytest.fixture()
def single_qr():
    with open("tests/fixtures/qrdata/single_qr.json", "r") as f:
        vector = json.load(f)
    return vector

class TestGenericReassembler(object):

    def test_bcur_single(self, bcur_singles):
        for bcur_single in bcur_singles:
            self.reassemble(
                bcur_single["urls"], 
                bcur_single["data"])

    def test_bcur_single(self, bcur_multi):
        self.reassemble(
            bcur_multi["urls"], 
            bcur_multi["data"])

    def test_single_qr(self, single_qr):
        data = single_qr[0]
        self.reassemble(
            [data],
            data)

    def reassemble(self, payloads, expected):
        reassembler = GenericReassembler()

        assert reassembler.total is None
        assert reassembler.type is None

        for payload in payloads:
            assert not reassembler.is_complete()
            assert reassembler.collect(payload) is True
            assert reassembler.type is not None
            assert reassembler.total == len(payloads)

        assert reassembler.is_complete() is True
        assert reassembler.decode() == expected
