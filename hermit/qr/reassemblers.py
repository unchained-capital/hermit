from base64 import b64decode
from typing import Optional
import re

from buidl.bcur import BCURMulti, BCURSingle

from ..errors import InvalidQRCodeSequence


class Reassembler:
    """Base class for QR code sequence reassemblers.

    Generalizes the process of reassembling N QR codes' payloads that
    may arive out of sequence.

    """

    def __init__(self):
        self.total_items = None
        self.segments = None
        self.data = None

    @classmethod
    def match_data(cls, data: str):
        """Tells whether or not the QR payload data matches the regular
        expression defining a particular type of QR encoding.

        """
        return cls.RE.match(data)

    def collect(self, data: str) -> bool:
        """Collect the given data.

        Will validate the data looks like it's part of the sequence
        being reassembled.

        Returns a tuple with the total number of data items in the
        sequence and the number collected so far.

        If the item cannot be collected, returns a tuple `(None,
        None)`.

        """
        match = self.match_data(data)
        if not match:
            raise InvalidQRCodeSequence("Data does not match QR code type.")

        total, index, segment = self._get_total_index_segment(match, data)

        return self._store_item(total, index, segment)

    def is_complete(self) -> bool:
        return self.total_items is not None and self.total_items == self.segments

    @property
    def total(self) -> int:
        return self.total_items

    def decode(self) -> str:
        """Assumbles all of the QR data segments into a the final
        payload."""

        if not self.is_complete():
            raise InvalidQRCodeSequence("Barcode value not complete.")

        return self._decode()

    def _get_total_index_segment(self, match, data: str) -> (int, int, str):
        raise NotImpementedException

    def _store_item(self, total: int, index: int, segment: str) -> bool:
        """Given the data from the regex match, store information
        about the current data item

        Returns a tuple with the total number of data items in the
        sequence and the number collected so far.

        If the item cannot be collected, returns a tuple `(None,
        None)`.

        """
        if self.total_items is None:
            self.total_items = total
            self.data = [None] * self.total
            self.segments = 0

        if self.total_items != total:
            raise InvalidQRCodeSequence("Mismatched QR sequence.")

        if self.data[index] is None:
            self.data[index] = segment
            self.segments += 1
            return True

        return False

    def _decode(self, match, data: str) -> str:
        """Do whatever implementation specific task needed to decode
        the multi segment payload data."""
        raise NotImpementedException


class SingleQRCodeReassembler(Reassembler):
    """Reassembles data from a single QR code.

    Just grabs whatever data is in the first QR code that we see and
    calls it complete.

    """

    RE = re.compile("^.*$", re.MULTILINE)
    TYPE = "QR"

    def _get_total_index_segment(self, match, data: str) -> (int, int, str):
        return 1, 0, data

    def _decode(self) -> str:
        return self.data[0]


class BCURSingleReassembler(Reassembler):
    """Reassembles data from BCUR single QR codes."""

    RE = re.compile("^ur:bytes/[^/]+/[^/]+$", re.IGNORECASE)
    TYPE = "BCUR"

    def _get_total_index_segment(self, match, data) -> (int, int, str):
        return 1, 0, data

    def _decode(self) -> str:
        return b64decode(BCURSingle.parse(self.data[0]).text_b64).decode("utf8")


class BCURMultiReassembler(Reassembler):
    """Reassembles data from BCUR QR code sequences."""

    RE = re.compile("^ur:bytes/([0-9]+)of([0-9]+)/[^/]+/[^/]+$", re.IGNORECASE)
    TYPE = "BCUR*"

    def _get_total_index_segment(self, match, data) -> (int, int, str):
        return int(match[2]), int(match[1]) - 1, data

    def _decode(self) -> str:
        # FIXME something strange happening here...
        base64_text = BCURMulti.parse(self.data).text_b64
        plain_bytes = b64decode(base64_text)
        try:
            return plain_bytes.decode("utf8")
        except UnicodeDecodeError:
            return base64_text


class SpecterDesktopReassembler(Reassembler):
    """Reassembles data from Specter Desktop QR code sequences."""

    RE = re.compile("^p([0-9]+)of([0-9]+) (.+)$")
    TYPE = "Specter"

    def _get_total_index_segment(self, match, data) -> (int, int, str):
        return int(match[2]), int(match[1]) - 1, data

    def _decode(self) -> str:
        return "".join(self.data)


class GenericReassembler:
    """Reassembles data split into a sequence of QR codes.

    The first payload is used to classify the nature of the QR code
    sequence (see :attr:`QRTYPES`).

    There are numerous scenarios where mixing up QR code sequence
    types will lead to both detectable and undedectable errors.

    """

    #: Classes defining QR code sequence types this reassembler
    #: understands.
    #:
    #: See the corresponding class for more information.
    REASSEMBLERS = [
        BCURSingleReassembler,
        BCURMultiReassembler,
        SpecterDesktopReassembler,  # Used for both psbts and accountmaps
        SingleQRCodeReassembler,  # This should always be at the end, because it always matches.
    ]

    def __init__(self):
        self.reassembler = None

    @property
    def total(self) -> str:
        return self.reassembler and self.reassembler.total

    @property
    def type(self):
        return self.reassembler and self.reassembler.TYPE

    def collect(self, data: str) -> bool:
        if self.reassembler is None:
            for cls in self.REASSEMBLERS:
                if cls.match_data(data):
                    self.reassembler = cls()
                    break
            if self.reassembler is None:
                raise InvalidQRCodeSequence("Unrecognized QR code format.")

        return self.reassembler.collect(data)

    def is_complete(self):
        return self.reassembler is not None and self.reassembler.is_complete()

    def decode(self):
        if self.reassembler is None:
            return None
        else:
            return self.reassembler.decode()
