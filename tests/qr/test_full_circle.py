from base64 import b64encode
from hermit.qr import (
    create_qr_sequence,
    GenericReassembler,
    qr_to_image,
    detect_qrs_in_image,
)


class TestQRFullCircle(object):
    def test_plain_text(self):
        data = "foobar"
        sequence = create_qr_sequence(data)
        reassembler = GenericReassembler()
        for qr in sequence:
            image = qr_to_image(qr)
            image = image.convert("RGBA")
            mirror, payloads = detect_qrs_in_image(image)
            for payload in payloads:
                reassembler.collect(payload)
                assert reassembler.total == len(sequence)
        assert reassembler.is_complete()
        assert reassembler.decode() == data

    def test_base64_text(self):
        data = "foobar"
        base64_data = b64encode(data.encode("utf8")).decode("utf8")
        sequence = create_qr_sequence(base64_data=base64_data)
        reassembler = GenericReassembler()
        for qr in sequence:
            image = qr_to_image(qr)
            image = image.convert("RGBA")
            mirror, payloads = detect_qrs_in_image(image)
            for payload in payloads:
                reassembler.collect(payload)
                assert reassembler.total == len(sequence)
        assert reassembler.is_complete()
        assert reassembler.decode() == data
