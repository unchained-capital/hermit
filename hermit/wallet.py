from buidl.hd import (
    HDPrivateKey,
    HDPublicKey,
)
from mnemonic import Mnemonic
from hermit import shards
from hermit.errors import HermitError
from hermit.qrcode import reader


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
            hd_obj = HDPrivateKey.from_seed(seed)
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

    def extended_public_key(
        self, bip32_path: str, testnet: bool = False, use_slip132: bool = False
    ) -> str:
        # hopefully, slip132 will be deprecated one day and this can be removed, BUT
        # for now it is the only way to guarantee seemless Specter-Desktop compatibility when uploading an xpub (on setup) from Hermit
        # https://github.com/satoshilabs/slips/blob/master/slip-0132.md#registered-hd-version-bytes

        # Will use whatever network the xpriv/trpiv is saved as from the unlock method
        self.unlock(testnet=testnet)
        hd_pubkey_obj = self._extended_public_key_obj(
            bip32_path=bip32_path, testnet=testnet
        )

        if use_slip132:
            if testnet is True:
                p2wsh_version_byte = "02575483"
            else:
                p2wsh_version_byte = "02aa7ed3"
            version = bytes.fromhex(p2wsh_version_byte)
        else:
            # This will automatically determine if we are xpub or tpub
            version = None

        return hd_pubkey_obj.xpub(version=version)

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
        # TODO: this should be persisted along with shamir shares, but the way Hermit handles persistance is hackey (os.system() calls)
        # Also, persistance is currently on the shards class and not the Wallet class

        if not account_map_str:
            # Get unsigned PSBT from webcam (QR gif) if not already passed in as an argument
            account_map_str = reader.read_qr_code("Scan the accountmap.")

        # Will use whatever network the xpriv/trpiv is saved as from the unlock method
        wsh_dict = parse_wshsortedmulti(output_record=account_map_str)

        # Confirm that our key is in this account map
        included = False
        for key_record in wsh_dict["key_records"]:
            # TODO: performance optimize this for large multisigs (99% of multisig re-uses the same paths)
            calculated_xpub = self.extended_public_key(
                bip32_path=key_record["path"], testnet=testnet, use_slip132=False
            )
            if calculated_xpub == key_record["xpub_parent"]:
                included = True
                break

            if calculated_xpub[:4] != key_record["xpub_parent"][:4]:
                # TODO: better way to convey this back to user?
                print(
                    f"Network mismatch: account map has {key_record['xpub_parent'][:4]} and we are looking for {calculated_xpub[:4]}."
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

    def has_account_map(self):
        return self.quorum_m > 0

    def derive_child_address(
        self,
        testnet: bool = False,
        is_change: bool = False,
        offset: int = 0,
        limit: int = 10,
    ):
        return None
        # return generate_wshsortedmulti_address(
            # quorum_m=self.quorum_m,
            # key_records=self.pubkey_records,
            # is_testnet=testnet,
            # is_change=is_change,
            # offset=offset,
            # limit=limit,
        # )
