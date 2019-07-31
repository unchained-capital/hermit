import unittest
from unittest.mock import Mock

from hermit.shards import Shard

class TestShard(object):

    def setup(self):
        self.interface = Mock()

    def test_create_shard(self, encrypted_mnemonic_1):
        shard_name = 'foo'

        shard = Shard(shard_name, encrypted_mnemonic_1, self.interface)

        assert shard.name == shard_name
        assert shard.encrypted_mnemonic == encrypted_mnemonic_1

    def test_decrypt_shard(self, encrypted_mnemonic_1, password_1, unencrypted_mnemonic_1):
        shard = Shard('foo', encrypted_mnemonic_1, self.interface)
        self.interface.get_password.return_value = password_1

        assert shard.words() == unencrypted_mnemonic_1

    def test_reencrypt_shard(self, encrypted_mnemonic_1, password_1, password_2, unencrypted_mnemonic_1):
        shard = Shard('foo', encrypted_mnemonic_1, self.interface)

        # set up the user inteface for two calls to 'get_change_password'. Once
        # to change from PASSWORD_1 to PASSWORD_2, and the second time to change
        # back.
        self.interface.get_change_password.side_effect = [(password_1, password_2), (password_2, password_1)]

        shard.change_password()
        mnemonic = shard.encrypted_mnemonic
        shard.change_password()

        # We should have the same encrypted mnemonic that we started with
        assert shard.encrypted_mnemonic == encrypted_mnemonic_1

        # The intermidiate mnemonic should be different
        assert mnemonic != encrypted_mnemonic_1
        assert mnemonic != unencrypted_mnemonic_1

    def test_shard_to_bytes(self, encrypted_mnemonic_1):
        shard = Shard('foo', encrypted_mnemonic_1, self.interface)
        byte_data = shard.to_bytes()
        # The byte representation of a shamir share varies a little based on the
        # payload, but for us, we are using 256-bit secrets, so this should give
        # us 33 word shares (256 / 10 rounds up to 26, plus 4 words for
        # bookkeeping and 3 for CRC gives 33). Converting this to bytes rounds
        # up to 42 bytes
        assert len(byte_data) == 42

    def test_shard_from_bytes(self, encrypted_mnemonic_1):
        shard = Shard('foo', encrypted_mnemonic_1, self.interface)
        byte_data = shard.to_bytes()

        shard2 = Shard('a', None, self.interface)
        shard2.from_bytes(byte_data)
        assert shard2.name == 'a'
        assert shard2.encrypted_mnemonic == shard.encrypted_mnemonic

    def test_shard_to_str(self, encrypted_mnemonic_1):
        shard = Shard('NAME', encrypted_mnemonic_1, self.interface)
        string_value = shard.to_str()
        assert string_value == 'NAME (family:5610 group:3 member:4)'
