from typing import List, Optional, Tuple
import bson
from hermit import shamir_share
from .interface import ShardWordUserInterface

class Shard(object):
    """Represents a single Shamir shard.

    """

    @property
    def encrypted_mnemonic(self):
        """
        The encrypted mnemonic words representing this shard
        """
        return self._encrypted_mnemonic

    @encrypted_mnemonic.setter
    def encrypted_mnemonic(self, words):
        self._encrypted_mnemonic = words
        self._share_id = None

    @property
    def share_id(self):
        """
        An integer representing the share family that this shard belongs to.
        """
        if self._share_id is None:
            self._unpack_share()
        return self._share_id

    @property
    def shard_id(self):
        """
        A pair of integers representing the group index and the member index of
        this shard
        """
        if self._group_id is None:
            self._unpack_share()
        return (self._group_id, self._member_id)

    def __init__(self,
                 name: str,
                 encrypted_mnemonic: Optional[str],
                 interface: ShardWordUserInterface = None,
                 ) -> None:
        """Creates a WalletWordsShard instance

        :param name: the name of the shard

        :param encrypted_mnemonic: the encrypted form of the mnemonic words for the share

        :param interface (optional): the interface used to communicate
        with the user about shard information. If none is given, the
        default WalletWordUserInterface is used.

        """
        self.name = name
        self._encrypted_mnemonic = encrypted_mnemonic
        self._share_id = None
        self._group_id = None
        self._member_id = None

        if interface is None:
            self.interface = ShardWordUserInterface()
        else:
            self.interface = interface

    def input(self) -> None:
        """Input this shard's data from a SLIP39 phrase"""
        words = self.interface.enter_shard_words(self.name)
        shamir_share.decode_mnemonic(words)
        self.encrypted_mnemonic = words

    def words(self) -> List[str]:
        """Returns the (decrypted) SLIP39 phrase for this shard"""
        return shamir_share.decrypt_mnemonic(self.encrypted_mnemonic, self._get_password())

    def change_password(self):
        """Decrypt and re-encrypt this shard with a new password"""
        old_password, new_password = self._get_change_password()

        self.encrypted_mnemonic = shamir_share.reencrypt_mnemonic(
            self.encrypted_mnemonic, old_password, new_password)
        self.encrypted_shard = shamir_share.decode_mnemonic(
            self.encrypted_mnemonic)

    def from_bytes(self, bytes_data: bytes) -> None:
        """Initialize shard from the given bytes"""
        self.encrypted_mnemonic = shamir_share.mnemonic_from_bytes(bytes_data)
        self.encrypted_shard = shamir_share.decode_mnemonic(
            self.encrypted_mnemonic)

    def to_bytes(self) -> bytes:
        """Serialize this shard to bytes"""
        return shamir_share.mnemonic_to_bytes(self.encrypted_mnemonic)

    def to_qr_bson(self) -> bytes:
        """Serialize this shard as BSON, suitable for a QR code"""
        return bson.dumps({self.name: self.to_bytes()})

    def _unpack_share(self) -> None:
        (self._share_id, _, self._group_id, _, _, self._member_id, _,
         _) = shamir_share.decode_mnemonic(self.encrypted_mnemonic)

    def to_str(self) -> str:
        """Return a user friendly string describing this shard and its membership in a group"""
        (identifier, _, group_index, _, _, member_identifier, _,
         _) = shamir_share.decode_mnemonic(self.encrypted_mnemonic)
        return "{0} (family:{1} group:{2} member:{3})".format(self.name, identifier, group_index + 1, member_identifier + 1)

    def _get_password(self) -> bytes:
        """Prompt the user for this shard's password"""
        return self.interface.get_password(self.to_str())

    def _get_change_password(self) -> Tuple[bytes, bytes]:
        return self.interface.get_change_password(self.to_str())
