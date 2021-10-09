from unittest.mock import Mock
from pytest import raises
from buidl import HDPrivateKey

from hermit.wallet import HDWallet
from hermit.errors import HermitError
import hermit

class FakeShards:
    def __init__(self, words):
        self.words = words

    def wallet_words(self):
        return self.words


class TestHDWalletLocking(object):

    def setup(self):
        self.wallet = HDWallet()

    def test_wallet_starts_out_locked(self):
        assert not self.wallet.unlocked()

    def test_locked_wallet_can_be_locked(self):
        self.wallet.lock()
        assert not self.wallet.unlocked()

    def test_locked_wallet_can_be_unlocked_if_seed_is_valid(self, opensource_wallet_words):
        self.wallet.shards = FakeShards(opensource_wallet_words)
        self.wallet.unlock()
        assert self.wallet.unlocked()

    def test_locked_wallet_can_be_unlocked_if_seed_is_valid_with_passphrase(self, trezor_bip39_vectors):
        for v in trezor_bip39_vectors["english"]:
            wallet = HDWallet()
            wallet.shards = FakeShards(v[1])
            wallet.unlock(passphrase="TREZOR")
            xprv = wallet.root_xprv
            assert xprv == v[3]

    def test_locked_wallet_cannot_be_unlocked_if_seed_is_invalid(self):
        self.wallet.shards = FakeShards("foo bar")
        with raises(HermitError) as error:
            self.wallet.unlock()
        assert "failed checksum" in str(error)

    def test_unlocked_wallet_can_tell_when_unlocked(self):
        self.wallet._root_xprv = Mock()
        assert self.wallet.unlocked()

    def test_unlocked_wallet_can_be_unlocked(self):
        self.wallet._root_xprv = Mock()
        self.wallet.unlock()
        assert self.wallet.unlocked()


class TestHDWalletTraversal(object):

    def test_bip32_vectors(self, bip32_vectors):
        for seed in bip32_vectors:
            wallet = HDWallet()
            wallet.root_xprv = bip32_vectors[seed]["m"]["xprv"]
            for path in bip32_vectors[seed]:
                if path != "m":

                    # The test vectors file doesn't have private keys,
                    # just xprv, so we have do calculate the private
                    # key from the xprv ourselves here in order to
                    # compare
                    xprv = bip32_vectors[seed][path]["xprv"]
                    expected_private_key = HDPrivateKey.parse(xprv).private_key
                    private_key = wallet.private_key(path)
                    assert expected_private_key.hex() == private_key.hex()

                    xpub = wallet.xpub(path)
                    expected_xpub = bip32_vectors[seed][path]["xpub"]
                    assert xpub == expected_xpub

    def test_unchained_vectors(self, unchained_vectors):
        for seed in unchained_vectors:
            wallet = HDWallet()
            wallet.root_xprv = unchained_vectors[seed]["m"]["xprv"]
            for path in unchained_vectors[seed]:
                if path != "m":

                    # The test vectors file doesn't have private keys,
                    # just xprv, so we have do calculate the private
                    # key from the xprv ourselves here in order to
                    # compare
                    xprv = unchained_vectors[seed][path]["xprv"]
                    expected_private_key = HDPrivateKey.parse(xprv).private_key
                    private_key = wallet.private_key(path)
                    assert expected_private_key.hex() == private_key.hex()

                    xpub = wallet.xpub(path)
                    expected_xpub = unchained_vectors[seed][path]["xpub"]
                    assert xpub == expected_xpub
