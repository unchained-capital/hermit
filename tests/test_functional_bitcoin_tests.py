import json
from unittest.mock import patch

import pytest

import hermit
from hermit.signer import BitcoinSigner
from hermit.wallet import HDWallet

@pytest.mark.integration
@patch('hermit.signer.displayer.display_qr_code')    
@patch('hermit.signer.base.input')    
@patch('hermit.signer.reader.read_qr_code')
class TestBitcoinSigningIntegration(object):
    
    def test_opensouce_bitcoin_vector_0(self,
                                        mock_request,
                                        mock_input,
                                        mock_display_qr_code,
                                        fixture_opensource_shard_set,
                                        fixture_opensource_bitcoin_vector_0,
                                        capsys):
        # TODO: use an actual wallet_words_file
        # TODO: move to all opensource vectors
        test_vector = fixture_opensource_bitcoin_vector_0
        wallet = HDWallet()
        wallet.shards = fixture_opensource_shard_set
        mock_request.return_value = test_vector['request_json']
        mock_input.return_value = 'y'

        signer = BitcoinSigner(wallet)
        signer.sign(testnet=True)        
        captured = capsys.readouterr()        

        expected_display = test_vector['expected_display']
        expected_return = test_vector['expected_signature']

        mock_display_qr_code.assert_called_once()
        mock_display_qr_code.assert_called_with(json.dumps(expected_return),
                                                name='Signature')
        assert captured.out == expected_display
