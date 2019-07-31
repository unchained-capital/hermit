import json
from unittest.mock import patch, create_autospec

import pytest

import hermit
from hermit.signer import BitcoinSigner
from hermit.wallet import HDWallet

# TODO: mainnet test
# TODO: more test vectors - use bitcoin_multisig tests
# TODO: multi-input test
# TODO: generate_multisig_address tests


class FakeShards:
    def __init__(self, words):
        self.words = words

    def wallet_words(self):
        return self.words

        
@patch('hermit.signer.reader.read_qr_code')
class TestBitcoinSignerValidation(object):

    @pytest.fixture(autouse=True)
    def setup_wallet_and_request(self,
                                 fixture_opensource_bitcoin_vector_0,
                                 opensource_wallet_words):
        self.wallet = HDWallet()
        self.wallet.shards = FakeShards(opensource_wallet_words)
        self.request = fixture_opensource_bitcoin_vector_0['request']
    
    def test_no_redeem_script_is_error(self, mock_request):
        self.request.pop('redeem_script', None)
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)
        assert str(e_info.value) == "Invalid signature request: no redeem script."

    def test_non_hex_redeem_script_is_error(self, mock_request):
        self.request['redeem_script'] = 'deadbeefgh'
        mock_request.return_value = json.dumps(self.request)

        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: redeem script is not valid hex."
        assert str(e_info.value) == expected
            
    def test_odd_length_hex_redeem_script_is_error(self, mock_request):
        self.request['redeem_script'] = 'deadbeefa'
        mock_request.return_value = json.dumps(self.request)

        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: redeem script is not valid hex."
        assert str(e_info.value) == expected

    def test_no_inputs_is_error(self, mock_request):
        self.request.pop('inputs', None)
        mock_request.return_value = json.dumps(self.request)

        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        assert str(e_info.value) == "Invalid signature request: no inputs."
        
    def test_inputs_not_array_is_error(self, mock_request):
        self.request['inputs'] = 'deadbeef'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'] = 123
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'] = True
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'] = {'a':123, 'b':456}
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['inputs'] = None
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: inputs is not an array."
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected        

    def test_empty_inputs_array_is_error(self, mock_request):
        self.request['inputs'] = []
        mock_request.return_value = json.dumps(self.request)

        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: at least one input is required."
        assert str(e_info.value) == expected
        
    def test_input_amount_required(self, mock_request):
        self.request['inputs'][1].pop('amount', None)
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: no amount in input."
        assert str(e_info.value) == expected

    def test_input_amount_must_integer(self, mock_request):
        self.request['inputs'][1]['amount'] = 'a'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['amount'] = 1.2
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['inputs'][1]['amount'] = '1.2'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['amount'] = '1'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['amount'] = True
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['inputs'][1]['amount'] = None
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info6:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "input amount must be an integer (satoshis).")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected
        assert str(e_info6.value) == expected                


    def test_input_amount_must_positive(self, mock_request):
        self.request['inputs'][1]['amount'] = 0
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['amount'] = -1
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "invalid input amount.")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
            
    def test_input_txid_required(self, mock_request):
        self.request['inputs'][1].pop('txid', None)
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: no txid in input."
        assert str(e_info.value) == expected

    def test_invalid_length_input_txid_is_error(self, mock_request):
        self.request['inputs'][1]['txid'] = 'deadbeef'*8 + 'a'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['txid'] = 'deadbeef'*8
        self.request['inputs'][1]['txid'] = self.request['inputs'][1]['txid'][1:]        
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "txid must be 64 characters.")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected

    def test_non_hex_input_txid_is_error(self, mock_request):
        self.request['inputs'][1]['txid'] = 'deadbeeg'*8
        mock_request.return_value = json.dumps(self.request)

        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "input TXIDs must be hexadecimal strings.")
        assert str(e_info.value) == expected
        
    def test_input_index_required(self, mock_request):
        self.request['inputs'][1].pop('index', None)
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: no index in input."
        assert str(e_info.value) == expected

    def test_input_index_must_integer(self, mock_request):
        self.request['inputs'][1]['index'] = 'a'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['index'] = 1.2
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['inputs'][1]['index'] = '1.2'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['index'] = '1'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['inputs'][1]['index'] = True
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['inputs'][1]['index'] = None
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "input index must be an integer.")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected        
        
    def test_input_index_cannot_be_negative(self, mock_request):
        self.request['inputs'][1]['index'] = -1
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "invalid input index.")
        assert str(e_info.value) == expected

    def test_no_outputs_is_error(self, mock_request):
        self.request.pop('outputs', None)
        mock_request.return_value = json.dumps(self.request)

        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        assert str(e_info.value) == "Invalid signature request: no outputs."

    def test_outputs_not_array_is_error(self, mock_request):
        self.request['outputs'] = 'deadbeef'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'] = 123
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'] = True
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'] = {'a':123, 'b':456}
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['outputs'] = None
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: outputs is not an array."
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected        

    def test_empty_outputs_array_is_error(self, mock_request):
        self.request['outputs'] = []
        mock_request.return_value = json.dumps(self.request)

        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: at least one output is required."
        assert str(e_info.value) == expected
        
    def test_output_address_required(self, mock_request):
        self.request['outputs'][1].pop('address', None)
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: no address in output."
        assert str(e_info.value) == expected

    def test_output_address_must_be_base58(self, mock_request):
        self.request['outputs'][1]['address'] = 'aI'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'][1]['address'] = 1.2
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['outputs'][1]['address'] = '1.2'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'][1]['address'] = True
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['outputs'][1]['address'] = None
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "output addresses must be base58-encoded strings.")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected

    def test_output_address_must_be_base58check(self, mock_request):
        self.request['outputs'][1]['address'] = 'abcd'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'][1]['address'] = '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN3'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        expected = ("Invalid signature request: "
                    + "invalid output address checksum.")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        
    @patch('hermit.signer.displayer.display_qr_code')    
    @patch('hermit.signer.base.input')    
    def test_valid_output_address_types(self,
                                        mock_input,
                                        mock_display_qr_code,
                                        mock_request):
        mock_input.return_value = 'y'
        mock_request.return_value = json.dumps(self.request)
        BitcoinSigner(self.wallet).sign(testnet=True)
        
        self.request['outputs'][1]['address'] = "1Ma2DrB78K7jmAwaomqZNRMCvgQrNjE2QC"
        self.request['outputs'][0]['address'] = "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
        mock_request.return_value = json.dumps(self.request)
        BitcoinSigner(self.wallet).sign(testnet=False)


    def test_output_bech_addresses_error(self, mock_request):
        bech_addr = 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
        self.request['outputs'][0]['address'] = bech_addr
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=False)

        test_bech_addr = 'tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx'
        self.request['outputs'][0]['address'] = test_bech_addr
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        expected = ("Invalid signature request: "
                    + "bech32 addresses are unsupported (output).")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
                
    def test_wrong_network_address_type_errors(self, mock_request):
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:        
            BitcoinSigner(self.wallet).sign(testnet=False)

        self.request['outputs'][1]['address'] = "1Ma2DrB78K7jmAwaomqZNRMCvgQrNjE2QC"
        self.request['outputs'][0]['address'] = "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:        
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "invalid output address (check mainnet vs. testnet).")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
            
    def test_output_amount_required(self, mock_request):
        self.request['outputs'][1].pop('amount', None)
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = "Invalid signature request: no amount in output."
        assert str(e_info.value) == expected

    def test_output_amount_must_integer(self, mock_request):
        self.request['outputs'][1]['amount'] = 'a'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'][1]['amount'] = 1.2
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['outputs'][1]['amount'] = '1.2'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'][1]['amount'] = '1'
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'][1]['amount'] = True
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            BitcoinSigner(self.wallet).sign(testnet=True)
            
        self.request['outputs'][1]['amount'] = None
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info6:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "output amount must be an integer (satoshis).")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected
        assert str(e_info6.value) == expected                


    def test_output_amount_must_positive(self, mock_request):
        self.request['outputs'][1]['amount'] = 0
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        self.request['outputs'][1]['amount'] = -1
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "invalid output amount.")
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected

    def test_network_fee_must_be_positive(self, mock_request):
        self.request['outputs'][1]['amount'] = 99999999
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            BitcoinSigner(self.wallet).sign(testnet=True)

        expected = ("Invalid signature request: "
                    + "fee cannot be negative.")
        assert str(e_info1.value) == expected


        
