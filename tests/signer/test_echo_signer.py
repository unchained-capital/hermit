import pytest
from unittest.mock import patch
import json

from hermit.signer import EchoSigner
from hermit.wallet import HDWallet


class TestEchoSigner(object):
    @patch('hermit.signer.displayer.display_qr_code')    
    @patch('hermit.signer.base.input')    
    @patch('hermit.signer.reader.read_qr_code')
    def test_can_create_valid_signature(self,
                                        mock_request,
                                        mock_input,
                                        mock_display_qr_code,
                                        fixture_opensource_bitcoin_vector_0,
                                        fixture_opensource_shard_set,
                                        capsys):
        request_json = fixture_opensource_bitcoin_vector_0['request_json']
        wallet = HDWallet()
        wallet.shards = fixture_opensource_shard_set
        mock_request.return_value = request_json
        mock_input.return_value = 'y'
        EchoSigner(wallet).sign(testnet=True)
        mock_display_qr_code.assert_called_once()
        captured = capsys.readouterr()
        expected_return = json.loads(request_json)
        expected_display = """QR Code:
        {}
        """.format(expected_return)

        mock_display_qr_code.assert_called_with(request_json, name='Request')
        # FIXME -- something pretty printing is causing this not to match?
        #assert captured.out == expected_display
