""" Interface wrapper for bip32 functions

An abstraction to separate hermit from python bip32 libraries.
"""

from pycoin.encoding.bytes32 import to_bytes_32
from pycoin.symbols.btc import network as BTC
import base58


def bip32_ckd(xkey: str, index: int) -> str:
    if xkey[1:4] == 'prv':
        private = True
    else:
        private = False
    if index >= 2 ** 31:
        harden = True
        index -= 2 ** 31
    else:
        harden = False
    key = BTC.parse.bip32(xkey)
    child_key = key.subkey(i=index, is_hardened=harden)
    return child_key.hwif(as_private=private)


def bip32_privtopub(xprv: str) -> str:
    key = BTC.parse.bip32(xprv)
    return key.hwif()


def bip32_master_key(seed: bytes) -> str:
    key = BTC.keys.bip32_seed(seed)
    return key.hwif(as_private=True)


def bip32_deserialize(xkey: str) -> (bytes, int, bytes, int, bytes, bytes):
    xkey_bytes = base58.b58decode_check(xkey)
    key = BTC.parse.bip32(xkey)
    if key.secret_exponent():
        key_data = to_bytes_32(key.secret_exponent()) + b'\01'
    else:
        key_data = key.sec(is_compressed=True)
    return (xkey_bytes[:4],
            key.tree_depth(),
            key.parent_fingerprint(),
            key.child_index(),
            key.chain_code(),
            key_data)


def bip32_extract_key(xpub: str) -> str:
    key = BTC.parse.bip32(xpub)
    return key.sec().hex()
