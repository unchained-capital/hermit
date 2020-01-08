import json
from unittest.mock import patch, create_autospec

import pytest

from hermit.shards import ShardSet

@pytest.fixture()
def trezor_bip39_vectors():
    with open("tests/fixtures/trezor_bip39_vectors.json", 'r') as f:
        vectors = json.load(f)
    return vectors

@pytest.fixture()
def bip32_vectors():
    with open("tests/fixtures/bip32_vectors.json", 'r') as f:
        vectors = json.load(f)
    return vectors

@pytest.fixture()
def unchained_vectors():
    with open("tests/fixtures/unchained_vectors.json", 'r') as f:
        vectors = json.load(f)
    return vectors

@pytest.fixture()
def bitcoin_testnet_signature_request():
    with open("examples/signature_requests/bitcoin_testnet.json", 'r') as f:
        request = json.load(f)
    return json.dumps(request)

@pytest.fixture()
def opensource_wallet_words():
    return "merge alley lucky axis penalty manage latin gasp virus captain wheel deal chase fragile chapter boss zero dirt stadium tooth physical valve kid plunge"


@pytest.fixture()
def fixture_opensource_shards(opensource_wallet_words):
    mock_interface = create_autospec(WalletWordUserInterface)
    mock_shard1 = create_autospec(WalletWordsShard)
    mock_shard2 = create_autospec(WalletWordsShard)
    mock_shard1.name = 'shard1'
    mock_shard2.name = 'shard2'
    mock_shard1.number = 1
    mock_shard2.number = 2
    mock_shard1.count = 2
    mock_shard2.count = 2
    mock_shard1.words.return_value = opensource_wallet_words.split()[:6]
    mock_shard2.words.return_value = opensource_wallet_words.split()[6:]
    mock_shard1.to_str.return_value = "{0} ({1}/{2})".format(mock_shard1.name,
                                                             mock_shard1.number,
                                                             mock_shard1.count)
    mock_shard2.to_str.return_value = "{0} ({1}/{2})".format(mock_shard2.name,
                                                             mock_shard2.number,
                                                             mock_shard2.count)

    mock_shard1.to_json.return_value = json.dumps([0,2,'encrypted1','salt1'])
    mock_shard2.to_json.return_value = json.dumps([1,2,'encrypted2','salt2'])

    mock_shards = {mock_shard1.name: mock_shard1,
                   mock_shard2.name: mock_shard2}
    return mock_shards

@pytest.fixture()
def fixture_opensource_shard_set(opensource_wallet_words):
    mock_shard_set = create_autospec(ShardSet)
    mock_shard_set.wallet_words.return_value = opensource_wallet_words
    return mock_shard_set

def prep_full_vector(filename):
    with open(filename, 'r') as f:
        test_vector = json.load(f)
    test_vector['request_json'] = json.dumps(test_vector['request'])
    test_vector['expected_display'] = (test_vector['expected_display']
                                       + json.dumps(test_vector['expected_signature'],
                                                    indent=2)
                                       + "\n")
    return test_vector

@pytest.fixture()
def fixture_opensource_bitcoin_vector_0():
    return prep_full_vector("tests/fixtures/opensource_bitcoin_test_vector_0.json")

