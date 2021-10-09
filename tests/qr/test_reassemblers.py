import pytest
import json

from hermit.qr import GenericReassembler

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


class TestGenericReassembler(object):

    def test_reassemble_all(self, test_qr_set):
        reassembler = GenericReassembler()

        assert reassembler.total is None
        assert reassembler.type is None

        for qr in test_qr_set:
            assert not reassembler.is_complete()
            assert reassembler.collect(qr) is True
            assert reassembler.type is not None
            assert reassembler.total is not None

        assert reassembler.is_complete() is True
        assert reassembler.decode() is not None

