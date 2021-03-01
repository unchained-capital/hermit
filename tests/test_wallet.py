import json
import pytest

from hermit.wallet import HDWallet
import hermit


class FakeShards:
    def __init__(self, words):
        self.words = words

    def wallet_words(self):
        return self.words


class TestCompressedPrivateKeyFromBIP32(object):
    pass


class TestCompressedPublickKeyFromBIP32(object):
    pass


class TestHardened(object):
    pass


class TestDecodeSegment(object):
    pass


class TestBIP32Sequence(object):
    def test_invalid_BIP32_paths_raise_error(self):
        bip32_path = "m/123/"
        with pytest.raises(hermit.errors.HermitError) as e_info1:
            hermit.wallet.bip32_sequence(bip32_path)

        bip32_path = "123'/1234/12"
        with pytest.raises(hermit.errors.HermitError) as e_info2:
            hermit.wallet.bip32_sequence(bip32_path)

        bip32_path = "m"
        with pytest.raises(hermit.errors.HermitError) as e_info3:
            hermit.wallet.bip32_sequence(bip32_path)

        bip32_path = "m123/123'/123/43"
        with pytest.raises(hermit.errors.HermitError) as e_info4:
            hermit.wallet.bip32_sequence(bip32_path)

        bip32_path = "m/123'/12''/12/123"
        with pytest.raises(hermit.errors.HermitError) as e_info5:
            hermit.wallet.bip32_sequence(bip32_path)

        bip32_path = "m/123'/12'/-12/123"
        with pytest.raises(hermit.errors.HermitError) as e_info6:
            hermit.wallet.bip32_sequence(bip32_path)

        expected = "Not a valid BIP32 path."
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected
        assert str(e_info6.value) == expected


class TestHDWalletInit(object):
    pass


class TestHDWalletUnlocked(object):
    def test_unlocked_wallet_is_unlocked(self, opensource_wallet_words):
        wallet = HDWallet()
        wallet.shards = FakeShards(opensource_wallet_words)
        wallet.unlock()
        assert wallet.unlocked() == True

    def test_init_wallet_is_not_unlocked(self):
        wallet = HDWallet()
        assert wallet.unlocked() == False

    def test_locked_wallet_is_not_unlocked(self, opensource_wallet_words):
        wallet = HDWallet()
        wallet.shards = FakeShards(opensource_wallet_words)
        wallet.unlock()
        wallet.lock()
        assert wallet.unlocked() == False


class TestHDWalletUnlock(object):
    def test_root_priv_from_trezor_vectors(self, trezor_bip39_vectors):
        # With Passphrase
        for v in trezor_bip39_vectors["english"]:
            wallet = HDWallet()
            wallet.shards = FakeShards(v[1])
            wallet.unlock(passphrase="TREZOR")
            xprv = wallet.root_priv
            assert xprv == v[3]

    def test_root_priv_from_unchained_vectors(self, unchained_vectors):
        # Without Passphrase
        for words in unchained_vectors:
            wallet = HDWallet()
            wallet.shards = FakeShards(words)
            wallet.unlock()
            xprv = wallet.root_priv
            expected_xprv = unchained_vectors[words]["m"]["xprv"]
            assert xprv == expected_xprv

    def test_checksum_failed_raises_error(self):
        wallet = HDWallet()

        # https://github.com/trezor/python-mnemonic/blob/master/test_mnemonic.py
        wallet.shards = FakeShards(
            "bless cloud wheel regular tiny venue"
            + "bird web grief security dignity zoo"
        )
        with pytest.raises(hermit.errors.HermitError) as e_info1:
            wallet.unlock()

        # https://github.com/kristovatlas/bip39_gym/blob/master/test_bip39.py
        wallet.shards = FakeShards("town iron abandon")
        with pytest.raises(hermit.errors.HermitError) as e_info2:
            wallet.unlock()

        # https://github.com/tyler-smith/go-bip39/blob/master/bip39_test.go
        wallet.shards = FakeShards(
            "abandon abandon abandon abandon abandon"
            + "abandon abandon abandon abandon abandon"
            + "abandon yellow"
        )
        with pytest.raises(hermit.errors.HermitError) as e_info3:
            wallet.unlock()

        expected = "Wallet words failed checksum."
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected


class TestHDWalletExtendedPublicKey(object):
    def test_bip32_vectors(self, bip32_vectors):
        for seed in bip32_vectors:
            wallet = HDWallet()
            wallet.root_priv = bip32_vectors[seed]["m"]["xprv"]
            for path in bip32_vectors[seed]:
                if path != "m":
                    xpub = wallet.extended_public_key(path)
                    expected_xpub = bip32_vectors[seed][path]["xpub"]
                    assert xpub == expected_xpub


class TestHDWalletPublicKey(object):
    def test_bip32_vectors(self, bip32_vectors):
        for seed in bip32_vectors:
            wallet = HDWallet()
            wallet.root_priv = bip32_vectors[seed]["m"]["xprv"]
            for path in bip32_vectors[seed]:
                if path != "m":
                    pubkey = wallet.public_key(path)
                    expected_pubkey = bip32_vectors[seed][path]["pubkey"]
                    assert pubkey == expected_pubkey


class TestHDWalletExtendedPrivateKey(object):
    def test_bip32_vectors(self, bip32_vectors):
        for seed in bip32_vectors:
            wallet = HDWallet()
            wallet.root_priv = bip32_vectors[seed]["m"]["xprv"]
            for path in bip32_vectors[seed]:
                if path != "m":
                    xprv = wallet.extended_private_key(path)
                    expected_xprv = bip32_vectors[seed][path]["xprv"]
                    assert xprv == expected_xprv
