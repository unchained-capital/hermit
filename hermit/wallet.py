from buidl.hd import (
    generate_wshsortedmulti_address,
    HDPrivateKey,
    HDPublicKey,
    parse_wshsortedmulti,
)
from mnemonic import Mnemonic
from hermit import shards
from hermit.errors import HermitError


class HDWallet(object):
    """Represents a hierarchical deterministic (HD) wallet

    Before the wallet can be used, its root private key must be
    reconstructed by unlocking a sufficient set of shards.
    """

    def __init__(self) -> None:
        self.root_xpriv = None
        self.xfp_hex = None  # root fingerprint in hex
        self.shards = shards.ShardSet()
        self.language = "english"
        # quorum m of all the public key records make up the account map (output descriptor) to use for validating a change/receive address:
        self.pubkey_records = []
        self.quorum_m = 0
        self.hdpubkey_map = {}

    def unlocked(self) -> bool:
        return self.root_xpriv is not None

    def unlock(self, passphrase: str = "", testnet: bool = False) -> None:
        if self.root_xpriv is not None:
            return

        mnemonic = Mnemonic(self.language)

        # TODO skip wallet words
        words = self.shards.wallet_words()
        if mnemonic.check(words):
            seed = Mnemonic.to_seed(words, passphrase=passphrase)
            hd_obj = HDPrivateKey.from_seed(seed, testnet=testnet)
            # Note that xprv conveys network info (xprv vs tprv) and this is only reset on locking/unlocking the wallet
            # TODO: a more elegant way to persist this data?
            self.root_xpriv = hd_obj.xprv()
            self.xfp_hex = (
                hd_obj.fingerprint().hex()
            )  # later needed to identify us as cosigner
        else:
            raise HermitError("Wallet words failed checksum.")

    def lock(self) -> None:
        self.root_xpriv = None

    def _extended_public_key_obj(self, bip32_path: str, testnet: bool = False) -> str:
        # Will use whatever network the xpriv/trpiv is saved as from the unlock method
        self.unlock(testnet=testnet)
        return HDPrivateKey.parse(self.root_xpriv).traverse(path=bip32_path).pub

    def extended_public_key(self, bip32_path: str, testnet: bool = False) -> str:
        # Will use whatever network the xpriv/trpiv is saved as from the unlock method
        self.unlock(testnet=testnet)
        hd_pubkey_obj = self._extended_public_key_obj(
            bip32_path=bip32_path, testnet=testnet
        )
        # buidl will automatically display xpub or tpub based on HDPrivateKey's network:
        return hd_pubkey_obj.xpub()

    def get_child_private_key_objs(self, bip32_paths):
        """
        Derive child private key objects and return them to (co)sign a transaction.
        """
        hd_priv_obj = HDPrivateKey.parse(self.root_xpriv)
        return [
            hd_priv_obj.traverse(bip32_path).private_key for bip32_path in bip32_paths
        ]

    def set_account_map(self, account_map_str: str, testnet: bool = False) -> bool:
        """
        Returns True if we were able to set the account map, False otherwise

        We would get False if the account map were invalid or our seed was not a part of it
        """
        # Will use whatever network the xpriv/trpiv is saved as from the unlock method
        wsh_dict = parse_wshsortedmulti(output_record=account_map_str)

        # Confirm that our key is in this account map
        included = False
        for key_record in wsh_dict["key_records"]:
            # TODO: performance optimize this for large multisigs (99% of multisig re-uses the same paths)
            calculated_xpub = self.extended_public_key(
                bip32_path=key_record["path"], testnet=testnet
            )
            if calculated_xpub == key_record["xpub_parent"]:
                included = True
                break

            if calculated_xpub[:4] != key_record["xpub_parent"][:4]:
                # TODO: better way to convey this back to user?
                print(
                    f"Network mistmatch: account map has {key_record['xpub_parent'][:4]} and we are looking for {calculated_xpub[:4]}."
                )
                print(f"Please toggle testnet and try again.")
                return False

        if not included:
            return False

        self.quorum_m = wsh_dict["quorum_m"]
        self.pubkey_records = wsh_dict["key_records"]
        hd_pubkey_map = {}
        for pubkey_record in self.pubkey_records:
            hd_pubkey_map[pubkey_record["xfp"]] = HDPublicKey.parse(
                pubkey_record["xpub_parent"]
            )
        self.hdpubkey_map = hd_pubkey_map
        return True

    def derive_child_address(
        self,
        testnet: bool = False,
        is_change: bool = False,
        offset: int = 0,
        limit: int = 10,
    ):
        return generate_wshsortedmulti_address(
            quorum_m=self.quorum_m,
            key_records=self.pubkey_records,
            is_testnet=testnet,
            is_change=is_change,
            offset=offset,
            limit=limit,
        )
