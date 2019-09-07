from base64 import b32decode, b32encode
from gzip import decompress, compress
from binascii import Error as Base32DecodeError


from hermit.errors import InvalidSignatureRequest


def decode_qr_code_data(encoded: bytes) -> str:
    if not isinstance(encoded, (bytes,)):
        raise InvalidSignatureRequest("Can only decode bytes")
    if encoded == b'':
        raise InvalidSignatureRequest("Cannot decode empty bytes")
    try:
        compressed_bytes = b32decode(encoded)
        try:
            decompressed_bytes = decompress(compressed_bytes)
            try:
                data = decompressed_bytes.decode('utf-8')
                return data
            except UnicodeError:
                raise InvalidSignatureRequest("Not valid UTF-8")
        except OSError:
            raise InvalidSignatureRequest("Not gzipped")
    except (TypeError, Base32DecodeError):
        raise InvalidSignatureRequest("Not Base32")


def encode_qr_code_data(decoded: str) -> bytes:
    if not isinstance(decoded, (str,)):
        raise InvalidSignatureRequest("Can only encode strings")
    if decoded.strip() == '':
        raise InvalidSignatureRequest("Cannot encode empty string")
    try:
        uncompressed_bytes = decoded.encode('utf-8')
        try:
            compressed_bytes = compress(uncompressed_bytes)
            try:
                data = b32encode(compressed_bytes)
                return data
            except TypeError:
                raise InvalidSignatureRequest("Failed to Base32-encode")
        except OSError:
            raise InvalidSignatureRequest("Failed to gzip")
    except UnicodeError:
        raise InvalidSignatureRequest("Failed to encode as UTF-8")
