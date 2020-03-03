from hermit.bip32 import (bip32_deserialize,
                          bip32_extract_key,
                          bip32_master_key,
                          bip32_privtopub,
                          bip32_ckd)


class TestDeriveBIP32ChildExtendedKey:

    def test_xpub_bip32_vectors(self, bip32_ckd_vectors):
        for seed in bip32_ckd_vectors:
            for path in bip32_ckd_vectors[seed]:
                expected_xprv = bip32_ckd_vectors[seed][path]['child_xprv']
                expected_xpub = bip32_ckd_vectors[seed][path]['child_xpub']
                res_xprv = bip32_ckd(
                    bip32_ckd_vectors[seed][path]['parent_xprv'],
                    bip32_ckd_vectors[seed][path]['index'])
                assert res_xprv == expected_xprv
                if path[-1] == "'":
                    pass
                else:
                    res_xpub = bip32_ckd(
                        bip32_ckd_vectors[seed][path]['parent_xpub'],
                        bip32_ckd_vectors[seed][path]['index'])
                    assert res_xpub == expected_xpub


class TestBIP32XprivToXpub:

    def test_bip32_vectors(self, bip32_vectors):
        for seed in bip32_vectors:
            for path in bip32_vectors[seed]:
                expected_xpub = bip32_vectors[seed][path]['xpub']
                res_xpub = bip32_privtopub(
                    bip32_vectors[seed][path]['xprv'])
                assert res_xpub == expected_xpub


class TestBIP32MasterKey:
    def test_bip32_vectors(self, bip32_vectors):
        for seed in bip32_vectors:
            expected_xprv = bip32_vectors[seed]['m']['xprv']
            res_xprv = bip32_master_key(bytes.fromhex(seed))
            assert expected_xprv == res_xprv


class TestBIP32Deserialize:

    def test_xpub_xprv(self):
        xpub = "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8" # noqa E501
        xprv = "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi" # noqa E501
        expected_xpub_de = (
            b'\x04\x88\xb2\x1e',
            0, b'\x00\x00\x00\x00',
            0,
            b"\x87=\xff\x81\xc0/RV#\xfd\x1f\xe5\x16~\xac:U\xa0I\xde=1K\xb4.\xe2'\xff\xed7\xd5\x08", # noqa E501
            b"\x039\xa3`\x130\x15\x97\xda\xefA\xfb\xe5\x93\xa0,\xc5\x13\xd0\xb5U'\xec-\xf1\x05\x0e.\x8f\xf4\x9c\x85\xc2") # noqa E501
        expected_xprv_de = (
            b'\x04\x88\xad\xe4',
            0,
            b'\x00\x00\x00\x00',
            0,
            b"\x87=\xff\x81\xc0/RV#\xfd\x1f\xe5\x16~\xac:U\xa0I\xde=1K\xb4.\xe2'\xff\xed7\xd5\x08", # noqa E501
            b'\xe8\xf3.r=\xec\xf4\x05\x1a\xef\xac\x8e,\x93\xc9\xc5\xb2\x1418\x17\xcd\xb0\x1a\x14\x94\xb9\x17\xc8Ck5\x01') # noqa E501
        assert bip32_deserialize(xpub) == expected_xpub_de
        assert bip32_deserialize(xprv) == expected_xprv_de


class TestBIP32ExtractKey:
    def test_bip32_vectors(self, bip32_vectors):
        for seed in bip32_vectors:
            for path in bip32_vectors[seed]:
                expected_pubkey = bip32_vectors[seed][path]['pubkey']
                pubkey = bip32_extract_key(bip32_vectors[seed][path]['xpub'])
                assert expected_pubkey == pubkey

# class TestHDWalletPublicKey(object):
#     def test_bip32_vectors(self, bip32_vectors):
#         for seed in bip32_vectors:
#             wallet = HDWallet()
#             wallet.root_priv = bip32_vectors[seed]['m']['xprv']
#             for path in bip32_vectors[seed]:
#                 if path != "m":
#                     pubkey = wallet.public_key(path)
#                     expected_pubkey = bip32_vectors[seed][path]['pubkey']
#                     assert pubkey == expected_pubkey
