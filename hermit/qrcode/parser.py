from typing import Optional

import re
from buidl.bcur import BCURMulti, BCURSingle

class ParserException(Exception):
    pass


# Generalize the process of collecting N qr codes that may arive out
# of sequence

class GenericParser:
    @classmethod
    def match_data(cls, data):
        """Tells whether or not the qr payload data matches the
        regular expression defining a particular type of QR encoding.
        """
        return cls.RE.match(data)

    def parse(self, data):
        """Parse the data from a qr payload and append it to the
        rest of the data obtained.
        """
        match = self.match_data(data)
        if not match:
            raise ParserException("Data does not match QR code type.")

        total, index, segment = self._get_total_index_segment(match, data)

        return self._store_item(total, index, segment)

    def __init__(self):
        self.total_items = None
        self.segments = None
        self.data = None

    def is_complete(self):
        return self.total_items is not None and self.total_items == self.segments

    @property
    def total(self):
        return self.total_items

    def decode(self):
        """Assumbles all of the qr data segments into a the final
        payload."""

        if not self.is_complete():
            raise ParserException("Barcode value not complete.")

        return self._decode()

    def _get_total_index_segment(self, match, data):
        raise NotImpementedException

    def _store_item(self, total, index, segment):
        if self.total_items is None:
            self.total_items = total
            self.data = [None] * self.total
            self.segments = 0

        if self.total_items != total:
            raise ParseException("mismatched qr sequence.")

        if self.data[index] is None:
            self.data[index] = segment
            self.segments += 1
            return f"Got {index+1} of {self.total}"

        return None

        """Given the data from the regex match, store information
        about the current data item."""

    def _decode(self, match, data):
        """Do whatever implementation specific task needed to decode
        the multi segment payload data."""
        raise NotImpementedException

class DefaultParser(GenericParser):
    """Just grab whatever data is in the first QR code that we see
    and call it complete."""

    RE = re.compile("^.*$")
    TYPE = "QR"

    def _get_total_index_segment(self, match, data):
        return 1,0,data

    def _decode(self):
        return self.data[0]

class BCURSingleParser(GenericParser):
    RE = re.compile("^ur:bytes/[^/]+/[^/]+$", re.IGNORECASE)
    TYPE = "BCUR"

    def _get_total_index_segment(self, match, data):
        return 1,0,data

    def _decode(self):
        return BCURSingle.parse(self.data[0]).text_b64

class BCURMultiParser(GenericParser):
    RE = re.compile("^ur:bytes/([0-9]+)of([0-9]+)/[^/]+/[^/]+$", re.IGNORECASE)
    TYPE = "BCUR*"

    def _get_total_index_segment(self, match, data):
        return int(match[2]), int(match[1])-1, data

    def _decode(self):
        return BCURMulti.parse(self.data).text_b64

class SpecterDesktopParser(GenericParser):
    RE = re.compile("^p([0-9]+)of([0-9]+) (.+)$")
    TYPE = "Specter"

    def _get_total_index_segment(self, match, data):
        return int(match[2]), int(match[1])-1, data

    def _decode(self):
        return "".join(self.data)


# The classes above each handle specific types of multi-QR encodings,
# the following class puts them all together. When we first encounter
# a qr code, we infer what type of encoding it containes from the contents
# and then try to put together the remainder of the segments.
#
# There are numerous scenarios where mixing up qr sequences will lead
# to both detectable and undedectable errors.

class QRParser:
    QRTYPES = [
        BCURSingleParser,
        BCURMultiParser,

        SpecterDesktopParser, # Used for both psbts and accountmaps

        DefaultParser, # This should always be at the end, because it always matches.
    ]

    def __init__(self):
        self.parser = None

    @property
    def total(self):
        return self.parser and self.parser.total

    @property
    def type(self):
        return self.parser and self.parser.TYPE

    def parse(self, data):
        if self.parser is None:
            for cls in self.QRTYPES:
                if cls.match_data(data):
                    self.parser = cls()
                    break
            if self.parser is None:
                raise ParserException("unrecognized qr format.")

        return self.parser.parse(data)

    def is_complete(self):
        return self.parser is not None and self.parser.is_complete()

    def decode(self):
        if self.parser is None:
            raise ParserException("qr sequence incomplete")
        else:
            return self.parser.decode()
