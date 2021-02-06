from buidl import HDPrivateKey, HDPublicKey
from mnemonic import Mnemonic

from hermit import shards
from hermit.errors import HermitError


class HDWallet(object):
    """Represents a hierarchical deterministic (HD) wallet

    Before the wallet can be used, its root private key must be
    reconstructed by unlocking a sufficient set of shards.
    """

    def __init__(self, testnet=False) -> None:
        self.root_xpriv = None
        self.xfp_hex = None  # root fingerprint in hex
        self.testnet = testnet
        self.shards = shards.ShardSet()
        self.language = "english"

    def unlocked(self) -> bool:
        return self.root_xpriv is not None

    def unlock(self, passphrase: str = "") -> None:
        if self.root_xpriv is not None:
            return

        mnemonic = Mnemonic(self.language)

        # TODO skip wallet words
        words = self.shards.wallet_words()
        if mnemonic.check(words):
            seed = Mnemonic.to_seed(words, passphrase=passphrase)
            hd_obj = HDPrivateKey.from_seed(seed, testnet=self.testnet)
            self.root_xpriv = hd_obj.xprv()
            self.xfp_hex = hd_obj.fingerprint().hex()  # later needed to identify us as cosigner
        else:
            raise HermitError("Wallet words failed checksum.")


    def lock(self) -> None:
        self.root_xpriv = None

    def extended_public_key(self, bip32_path: str) -> str:
        self.unlock()
        # TODO: do we want to allow passing in SLIP132 version byte (ypub/zpub)?
        # Going with default xpub ONLY for now
        return HDPrivateKey.parse(self.root_xpriv).traverse(path=bip32_path).xpub()

    def get_child_private_key_objs(self, bip32_paths):
        """
        Derive child private key objects and return them to (co)sign a transaction.
        """
        hd_priv_obj = HDPrivateKey.parse(self.root_xpriv)
        return [
            hd_priv_obj.traverse(bip32_path).private_key for bip32_path in bip32_paths
        ]
