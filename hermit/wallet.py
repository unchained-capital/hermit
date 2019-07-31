from re import match
from typing import Tuple

from mnemonic import Mnemonic
from pybitcointools import (bip32_ckd,
                            bip32_privtopub,
                            bip32_master_key,
                            bip32_deserialize,
                            bip32_extract_key)

from hermit import shards
from hermit.errors import HermitError


def compressed_private_key_from_bip32(bip32_xkey: str) -> bytes:
    """Return a compressed private key from the given BIP32 path"""
    bip32_args = bip32_deserialize(bip32_xkey)
    # cut off 'compressed' byte flag (only for private key!)
    return bip32_args[5][:-1]


def compressed_public_key_from_bip32(bip32_xkey: str) -> bytes:
    """Return a compressed public key from the given BIP32 path"""
    bip32_args = bip32_deserialize(bip32_xkey)
    return bip32_args[5]


def _hardened(id: int) -> int:
    hardening_offset = 2 ** 31
    return (hardening_offset + id)


def _decode_segment(segment: str) -> int:
    if segment.endswith("'"):
        return _hardened(int(segment[:-1]))
    else:
        return int(segment)


def bip32_sequence(bip32_path: str) -> Tuple[int, ...]:
    """Turn a BIP32 path into a tuple of deriviation points
    """
    bip32_path_regex = "^m(/[0-9]+'?)+$"

    if not match(bip32_path_regex, bip32_path):
        raise HermitError("Not a valid BIP32 path.")

    return tuple(
        _decode_segment(segment)
        for segment in bip32_path[2:].split('/')
        if len(segment) != 0)


class HDWallet(object):
    """Represents a hierarchical deterministic (HD) wallet

    Before the wallet can be used, its root private key must be
    reconstructed by unlocking a sufficient set of shards.
    """

    def __init__(self) -> None:
        self.root_priv = None
        self.shards = shards.ShardSet()
        self.language = "english"

    def unlocked(self) -> bool:
        return self.root_priv is not None

    def unlock(self, passphrase: str = "") -> None:
        if self.root_priv is not None:
            return

        mnemonic = Mnemonic(self.language)

        # TODO skip wallet words
        words = self.shards.wallet_words()
        if mnemonic.check(words):
            seed = Mnemonic.to_seed(words, passphrase=passphrase)
            self.root_priv = bip32_master_key(seed)
        else:
            raise HermitError("Wallet words failed checksum.")

    def lock(self) -> None:
        self.root_priv = None

    def extended_public_key(self, bip32_path: str) -> str:
        self.unlock()
        xprv = self.extended_private_key(bip32_path)
        return bip32_privtopub(xprv)

    def public_key(self, bip32_path: str) -> str:
        xpub = self.extended_public_key(bip32_path)
        return bip32_extract_key(xpub)

    def extended_private_key(self, bip32_path: str) -> str:
        self.unlock()
        xprv = self.root_priv
        for child_id in bip32_sequence(bip32_path):
            xprv = bip32_ckd(xprv, child_id)
        return str(xprv)
