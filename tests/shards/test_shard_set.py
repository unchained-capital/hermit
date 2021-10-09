import bson
import unittest
from unittest.mock import Mock, mock_open, call, patch

import hermit
from hermit.shards import ShardSet
from hermit.config import HermitConfig
import shamir_mnemonic


class TestShardSet(object):

    def setup(self):
        self.interface = Mock()
        self.config = HermitConfig()
        config_patch = patch(
            "hermit.shards.shard_set.get_config", return_value=self.config
        )

        self.config_patch = config_patch.start()

        self.rg = Mock()
        self.old_rg = hermit.shards.shard_set.RNG

        hermit.shards.shard_set.RNG = self.rg
        shamir_mnemonic.RANDOM_BYTES = self.rg.random

        # Keep track of how much random data was provisioned and used
        self.random_requested = 0
        self.random_provisioned = 0

        def mock_random(count):
            self.random_requested += count
            return b"0" * count

        def mock_ensure(count):
            self.random_provisioned += count

        self.rg.random.side_effect = mock_random
        self.rg.ensure_bytes = mock_ensure

    def teardown(self):
        # Clean up random number mocking
        hermit.shards.shard_set.RNG = self.old_rg
        shamir_mnemonic.RANDOM_BYTES = self.old_rg.random

        self.config_patch.stop()

        # Ensure that the random number ledgers are balanced.
        assert self.random_requested == self.random_provisioned

    def test_init(self):
        shard_set = ShardSet(self.interface)
        assert shard_set.shards == {}
        assert shard_set.config == self.config
        assert shard_set.interface == self.interface

    @unittest.skip("test not implemented")
    def test_ensure_shards(self):
        assert False

    @unittest.skip("test not implemented")
    def test_save(self):
        assert False

    def test_initialize_file(self):
        self.config.paths["shards_file"] = "shards file"
        shard_set = ShardSet(self.interface)

        with patch("builtins.open", mock_open()) as mock_file:
            shard_set.initialize_file()
            mock_file.assert_called_with("shards file", "wb")
            mock_file().write.called_with(bson.dumps({}))

    def test_create_from_random(self, password_1, password_2):
        self.interface.confirm_password.side_effect = [password_1, password_2, b"pw3"]
        self.interface.get_password.side_effect = [password_1, password_2, b"pw3"]
        self.interface.get_name_for_shard.side_effect = ["one", "two", "three"]
        self.interface.choose_shard.side_effect = ["one", "two", "three", None]
        self.interface.enter_group_information.return_value = [1, [(3, 3)]]

        shard_set = ShardSet(self.interface)
        shard_set._shards_loaded = True

        shard_set.create_random_share()

        result_words = shard_set.wallet_words()
        assert len(result_words.split(" ")) == 24

        assert self.interface.confirm_password.call_count == 3
        assert self.interface.get_password.call_count == 3

        get_password_calls = [
            call(shard.to_str()) for shard in shard_set.shards.values()
        ]
        assert self.interface.get_password.call_args_list == get_password_calls

        assert self.interface.get_name_for_shard.call_count == 3

        shareid = shard_set.shards["one"].share_id
        # group index 0, group threshold 1, groups 1, memberid changes, member threshold 2
        get_name_calls = [
            call(shareid, 0, 1, 1, i, 3, shard_set.shards) for i in range(3)
        ]
        assert self.interface.get_name_for_shard.call_args_list == get_name_calls

        assert self.interface.choose_shard.call_count == 3
        assert self.interface.enter_group_information.call_count == 1

        assert self.rg.random.call_args_list == [call(32), call(2), call(32), call(28)]

    def test_create_from_random_large_group(self):
        # Make all the passwords the same to make things easier
        self.interface.confirm_password.return_value = b"password"
        self.interface.get_password.return_value = b"password"

        self.interface.get_name_for_shard.side_effect = (str(x) for x in range(100))
        self.interface.enter_group_information.return_value = [
            3,
            [(7, 15), (7, 15), (7, 15), (7, 15)],
        ]

        shard_set = ShardSet(self.interface)
        shard_set._shards_loaded = True

        shard_set.create_random_share()

        assert self.interface.confirm_password.call_count == 15 * 4
        assert self.interface.get_name_for_shard.call_count == 15 * 4
        assert self.interface.enter_group_information.call_count == 1

        calls = (
            [
                call(32),
            ]
            + [  # master secret
                call(2),
            ]
            + [call(32), call(28)]  # identifier
            + ([call(32)] * 5 + [call(28)])  # group secrets (less digest)
            * 4  # member secrets (less digests)
        )
        assert self.rg.random.call_args_list == calls

    def test_create_from_wallet_words(self, zero_wallet_words, password_1, password_2):
        self.interface.enter_wallet_words.return_value = zero_wallet_words
        self.interface.confirm_password.side_effect = [password_1, password_2]
        self.interface.get_password.side_effect = [password_1, password_2]
        self.interface.get_name_for_shard.side_effect = ["one", "two"]
        self.interface.choose_shard.side_effect = ["one", "two"]
        self.interface.enter_group_information.return_value = [1, [(2, 2)]]

        shard_set = ShardSet(self.interface)
        shard_set._shards_loaded = True

        shard_set.create_share_from_wallet_words()

        result_words = shard_set.wallet_words()
        assert result_words == zero_wallet_words

        assert self.interface.enter_wallet_words.call_count == 1
        assert self.interface.confirm_password.call_count == 2
        assert self.interface.get_password.call_count == 2

        get_password_calls = [
            call(shard.to_str()) for shard in shard_set.shards.values()
        ]
        assert self.interface.get_password.call_args_list == get_password_calls

        assert self.interface.get_name_for_shard.call_count == 2

        shareid = shard_set.shards["one"].share_id
        # group index 0, group threshold 1, groups 1, memberid changes, member threshold 2
        get_name_calls = [
            call(shareid, 0, 1, 1, i, 2, shard_set.shards) for i in range(2)
        ]
        assert self.interface.get_name_for_shard.call_args_list == get_name_calls

        assert self.interface.choose_shard.call_count == 2
        assert self.interface.enter_group_information.call_count == 1

        assert self.rg.random.call_args_list == [call(2), call(28)]

    def test_get_secret_seed_from_wallet_words(
        self, zero_wallet_words, password_1, password_2
    ):
        self.interface.enter_wallet_words.return_value = zero_wallet_words
        self.interface.confirm_password.side_effect = [password_1, password_2]
        self.interface.get_password.side_effect = [password_1, password_2]
        self.interface.get_name_for_shard.side_effect = ["one", "two"]
        self.interface.choose_shard.side_effect = ["one", "two"]
        self.interface.enter_group_information.return_value = [1, [(2, 2)]]
        shard_set = ShardSet(self.interface)
        shard_set._shards_loaded = True

        shard_set.create_share_from_wallet_words()

        result_bytes = shard_set.secret_seed()
        assert result_bytes == b"\x00" * 32

        assert self.interface.enter_wallet_words.call_count == 1
        assert self.interface.confirm_password.call_count == 2
        assert self.interface.get_password.call_count == 2

        get_password_calls = [
            call(shard.to_str()) for shard in shard_set.shards.values()
        ]
        assert self.interface.get_password.call_args_list == get_password_calls

        assert self.interface.get_name_for_shard.call_count == 2

        shareid = shard_set.shards["one"].share_id
        # group index 0, group threshold 1, groups 1, memberid changes, member threshold 2
        get_name_calls = [
            call(shareid, 0, 1, 1, i, 2, shard_set.shards) for i in range(2)
        ]
        assert self.interface.get_name_for_shard.call_args_list == get_name_calls

        assert self.interface.choose_shard.call_count == 2
        assert self.interface.enter_group_information.call_count == 1

        assert self.rg.random.call_args_list == [call(2), call(28)]

    def test_get_secret_seed_complicated_groups_with_wallet_words(
        self, zero_wallet_words, zero_bytes
    ):

        # This is a somewhat complicated scenario.
        # We're going to generate a shamir share set from wallet words.
        # The set includes three groups, and two of the three groups need to be
        # represented in order to reconstitute the secret. Of the three groups,
        # one is a one of one. Another is a 2 of three. The last one is a 3 of
        # 5.
        #
        # Overall, there are 9 shards that have to be given unique names and
        # passwords.
        #
        # Then, to reconstitute the secret, we select two of the shards from the
        # second group and three of the shards from the third group. We unlock
        # each shard with its appropriate password and verify that the secret
        # that we recover matches what we started with.

        self.interface.enter_wallet_words.return_value = zero_wallet_words

        self.interface.confirm_password.side_effect = [
            b"0",
            b"1",
            b"2",
            b"3",
            b"4",
            b"5",
            b"6",
            b"7",
            b"8",
        ]
        self.interface.get_name_for_shard.side_effect = [
            "0",
            "10",
            "11",
            "12",
            "20",
            "21",
            "22",
            "23",
            "24",
        ]
        self.interface.choose_shard.side_effect = ["10", "12", "21", "22", "24"]
        self.interface.get_password.side_effect = [b"1", b"3", b"5", b"6", b"8"]
        self.interface.enter_group_information.return_value = [
            2,
            [(1, 1), (2, 3), (3, 5)],
        ]

        shard_set = ShardSet(self.interface)
        shard_set._shards_loaded = True

        shard_set.create_share_from_wallet_words()
        result_bytes = shard_set.secret_seed()
        assert result_bytes == zero_bytes

        assert self.interface.enter_wallet_words.call_count == 1
        assert self.interface.confirm_password.call_count == 9
        assert self.interface.get_password.call_count == 5

        share_id = shard_set.shards["0"].share_id
        calls = (
            [call(share_id, 0, 2, 3, 0, 1, shard_set.shards)]
            + [call(share_id, 1, 2, 3, i, 2, shard_set.shards) for i in range(3)]
            + [call(share_id, 2, 2, 3, i, 3, shard_set.shards) for i in range(5)]
        )

        assert self.interface.get_name_for_shard.call_args_list == calls
        assert self.interface.get_name_for_shard.call_count == 9

        assert self.interface.choose_shard.call_count == 5
        assert self.interface.enter_group_information.call_count == 1

        assert self.rg.random.call_args_list == [
            call(2),
            call(28),
            call(28),
            call(32),
            call(28),
        ]

    def test_enter_shard_words(self, encrypted_mnemonic_1):
        shard_set = ShardSet(interface=self.interface)
        shard_set._shards_loaded = True

        self.interface.enter_shard_words.return_value = encrypted_mnemonic_1

        shard_set.input_shard_words("x")

        assert self.interface.enter_shard_words.call_count == 1
        assert "x" in shard_set.shards
        assert shard_set.shards["x"].encrypted_mnemonic == encrypted_mnemonic_1
