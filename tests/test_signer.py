from unittest.mock import patch, Mock
from pytest import raises

from hermit import (
    Signer, 
    HDWallet, 
    HermitError,
    InvalidPSBT,
)

class TestSignerSign(object):

    def setup(self):
        self.wallet = HDWallet()
        self.signer = Signer(self.wallet)

# @pytest.mark.integration
# @patch("hermit.signer.display_data_as_animated_qrs")
# @patch("hermit.signer.base.input")
# @patch("hermit.signer.read_data_from_animated_qrs")
# class TestBitcoinSigningIntegration(object):
#     def test_opensouce_bitcoin_vector_0(
#             self,
#             mock_read_data_from_animated_qrs,
#             mock_input,
#             mock_display_data_as_animated_qrs,
#             fixture_opensource_shard_set,
#             fixture_opensource_bitcoin_vectors,
#             capsys,
#     ):
#         # TODO: use an actual shard_file
#         # TODO: move to all opensource vectors
#         test_vector = fixture_opensource_bitcoin_vectors
#         wallet = HDWallet()
#         wallet.shards = fixture_opensource_shard_set
#         mock_read_data_from_animated_qrs.return_value = test_vector["request_json"]
#         mock_input.return_value = "y"

#         signer = Signer(wallet)
#         signer.sign(testnet=True)
#         captured = capsys.readouterr()

#         expected_display = test_vector["expected_display"]
#         expected_return = test_vector["expected_signature"]

#         mock_display_qr_code.assert_called_once()
#         mock_display_qr_code.assert_called_with(
#             json.dumps(expected_return), name="Signature"
#         )

#         # assert captured.out == expected_display

        
class TestSignerSignatureRequestHandling(object):

    def setup(self):
        self.wallet = HDWallet()
        self.signer = Signer(self.wallet)
        self.unsigned_psbt_b64 = Mock()
        self.psbt = Mock()


    #
    # read_signature_request
    #


    @patch("hermit.signer.read_data_from_animated_qrs")
    def test_read_signature_request_with_unsigned_PSBT(self, mock_read_data_from_animated_qrs):
        signer = Signer(self.wallet, unsigned_psbt_b64=self.unsigned_psbt_b64)
        signer.read_signature_request()
        assert signer.unsigned_psbt_b64 == self.unsigned_psbt_b64
        mock_read_data_from_animated_qrs.assert_not_called()

    @patch("hermit.signer.read_data_from_animated_qrs")
    def test_read_signature_request_without_unsigned_PSBT(self, mock_read_data_from_animated_qrs):
        mock_read_data_from_animated_qrs.return_value = self.unsigned_psbt_b64
        self.signer.read_signature_request()
        assert self.signer.unsigned_psbt_b64 == self.unsigned_psbt_b64
        mock_read_data_from_animated_qrs.assert_called()

    #
    # parse_signature_request
    #

    def test_parse_signature_request_without_unsigned_PSBT(self):
        with raises(HermitError) as error:
            self.signer.parse_signature_request()
        assert "No PSBT" in str(error)

    @patch("hermit.signer.PSBT.parse_base64")
    def test_parse_signature_request_with_valid_PSBT(self, mock_parse_base64):
        self.signer.unsigned_psbt_b64 = self.unsigned_psbt_b64
        mock_parse_base64.return_value = self.psbt
        self.signer.parse_signature_request()
        assert self.signer.psbt == self.psbt
        mock_parse_base64.assert_called_once_with(self.unsigned_psbt_b64)

    @patch("hermit.signer.PSBT.parse_base64")
    def test_parse_signature_request_with_invalid_PSBT(self, mock_parse_base64):
        self.signer.unsigned_psbt_b64 = self.unsigned_psbt_b64
        mock_parse_base64.side_effect = RuntimeError("foobar")
        with raises(InvalidPSBT) as error:
            self.signer.parse_signature_request()
        assert "Invalid PSBT" in str(error)
        assert "RuntimeError" in str(error)
        assert "foobar" in str(error)
        mock_parse_base64.assert_called_once_with(self.unsigned_psbt_b64)

    #
    # validate_signature_request
    #

    def test_validate_signature_request(self):
        mock_validate = Mock()
        self.psbt.validate = mock_validate
        mock_validate.return_value = True
        self.signer.psbt = self.psbt
        self.signer.validate_signature_request()

    def test_validate_signature_request(self):
        mock_validate = Mock()
        self.psbt.validate = mock_validate
        mock_validate.return_value = False
        self.signer.psbt = self.psbt
        with raises(InvalidPSBT) as error:
            self.signer.validate_signature_request()
        assert "Invalid PSBT" in str(error)

class TestSignerTransactionDescription(object):

    def setup(self):
        self.wallet = HDWallet()
        self.xfp_hex = "deadbeefaa"
        self.wallet.xfp_hex = self.xfp_hex
        self.psbt = Mock()
        self.signer = Signer(self.wallet)
        self.signer.psbt = self.psbt
        self.metadata = dict(
            tx_summary_text="foobar",
            txid="this_txid",
            tx_fee_sats=100,
            locktime=0,
            version=1,
            inputs_desc=dict(
                inputs_desc=[
                    dict(
                        idx=0,
                        prev_txhash="input_prev_hash",
                        prev_idx=2,
                        sats=10000,
                    ),
                ],
            ),
            outputs_desc=dict(
                outputs_desc=[
                    dict(
                        idx=0,
                        addr="output address",
                        sats=5000,
                        is_change=False,
                    ),
                    dict(
                        idx=1,
                        addr="change address",
                        sats=4900,
                        is_change=True,
                    ),
                ],
            ),
        )

    @patch("hermit.signer.describe_basic_psbt")
    def test_generate_transaction_metadata(self, mock_describe_basic_psbt):
        mock_describe_basic_psbt.return_value = self.metadata
        self.signer.generate_transaction_metadata()
        assert self.signer.transaction_metadata == self.metadata
        mock_describe_basic_psbt.assert_called_once_with(
            self.psbt,
            xfp_for_signing=self.xfp_hex)

    def test_transaction_description_lines(self):
        self.signer.transaction_metadata = self.metadata
        assert self.signer.transaction_description_lines() == [
            "foobar",
            "",
            "TXID: this_txid",
            "Fee in Sats: 100",
            "Lock Time: 0",
            "Version: 1",
            "",
            "INPUTS:",
            "  Input 0:",
            "    Previous TX Hash: input_prev_hash",
            "    Previous Output Index: 2",
            "    Sats: 10,000",
            "",
            "OUTPUTS:",
            "  Output 0:",
            "    Address: output address",
            "    Sats: 5,000",
            "    Is Change?: False",
            "",
            "  Output 1:",
            "    Address: change address",
            "    Sats: 4,900",
            "    Is Change?: True",
            "",
        ]

    @patch("hermit.signer.print_formatted_text")
    def test_print_transaction_description(self, mock_print_formatted_text):
        with patch.object(self.signer, "transaction_description_lines") as mock_transaction_description_lines:
            mock_transaction_description_lines.return_value = ["line1", "line2", "line3"]
            self.signer.print_transaction_description()
            calls = mock_print_formatted_text.call_args_list
            assert len(calls) == 3
            for call in calls:
                assert len(call[0]) == 1
                assert call[1] == {}
            assert calls[0][0][0] == "line1"
            assert calls[1][0][0] == "line2"
            assert calls[2][0][0] == "line3"
            
class TestSignerApproveSignature(object):

    def setup(self):
        self.wallet = HDWallet()
        self.signer = Signer(self.wallet)
        self.yes = "Y eS"
        self.no = "anything else"

    def assert_prompt_call(self, mock):
        mock.assert_called_once()
        call = mock.call_args_list[0]
        assert len(call[0]) == 1
        assert "Sign the above transaction? [y/N]" in str(call[0][0])
        assert call[1] == {}

    #
    # With session
    #

    def test_approve_signature_request_with_session(self):
        mock_session = Mock()
        mock_prompt = Mock()
        mock_session.prompt = mock_prompt
        mock_prompt.return_value = self.yes
        self.signer.session = mock_session
        assert self.signer.approve_signature_request() is True
        self.assert_prompt_call(mock_prompt)

    def test_reject_signature_request_with_session(self):
        mock_session = Mock()
        mock_prompt = Mock()
        mock_session.prompt = mock_prompt
        mock_prompt.return_value = self.no
        self.signer.session = mock_session
        assert self.signer.approve_signature_request() is False
        self.assert_prompt_call(mock_prompt)

    #
    # Without session
    #

    @patch("hermit.signer.input")
    def test_approve_signature_request_without_session(self, mock_input):
        mock_input.return_value = self.yes
        assert self.signer.approve_signature_request() is True
        self.assert_prompt_call(mock_input)

    @patch("hermit.signer.input")
    def test_reject_signature_request_without_session(self, mock_input):
        mock_input.return_value = self.no
        assert self.signer.approve_signature_request() is False
        self.assert_prompt_call(mock_input)

class TestSignerCreateSignature(object):

    def setup(self):
        self.wallet = HDWallet()
        self.testnet = Mock()
        self.signer = Signer(self.wallet, testnet=self.testnet)
        self.psbt = Mock()
        self.signer.psbt = self.psbt
        self.signer.transaction_metadata = dict(
            root_paths=dict(
                xfp1=["m/45'/0'/0'"],
                xfp2=["m/45'/0'/0'"],
                xfp3=["m/45'/0'/1'"],
            ))
        self.mock_wallet_private_key = Mock()
        self.wallet.private_key = self.mock_wallet_private_key
        self.mock_private_keys = [Mock(), Mock(), Mock()]
        self.mock_wallet_private_key.side_effect = self.mock_private_keys

        self.mock_sign_with_private_keys = Mock()
        self.psbt.sign_with_private_keys = self.mock_sign_with_private_keys

    def teardown(self):
        self.mock_sign_with_private_keys.assert_called_once_with(
            private_keys=self.mock_private_keys)

        calls = self.mock_wallet_private_key.call_args_list
        assert len(calls) == 3
        for index, call in enumerate(calls):
            assert len(call[0]) == 1
            assert call[1] == dict(testnet=self.testnet)

        assert calls[0][0][0] == "m/45'/0'/0'"
        assert calls[1][0][0] == "m/45'/0'/0'"
        assert calls[2][0][0] == "m/45'/0'/1'"


    #
    # Create signature
    #

    def test_create_signature_successfully(self):
        self.mock_sign_with_private_keys.return_value = True

        mock_signed_psbt_b64 = Mock()
        mock_serialize_base64 = Mock()
        mock_serialize_base64.return_value = mock_signed_psbt_b64
        self.psbt.serialize_base64 = mock_serialize_base64

        self.signer.create_signature()
        assert self.signer.signed_psbt_b64 == mock_signed_psbt_b64

    def test_create_signature_unsuccessfully(self):
        self.mock_sign_with_private_keys.return_value = False

        with raises(HermitError) as error:
            self.signer.create_signature()
        assert "Failed to sign" in str(error)

class TestSignerShowSignature(object):

    @patch("hermit.signer.print_formatted_text")
    @patch("hermit.signer.display_data_as_animated_qrs")
    def test_show_signature(self, mock_display_data_as_animated_qrs, mock_print_formatted_text):
        wallet = HDWallet()
        signer = Signer(wallet)
        signed_psbt_b64 = "foobar"
        signer.signed_psbt_b64 = signed_psbt_b64
        signer.show_signature()

        calls = mock_print_formatted_text.call_args_list
        assert len(calls) == 2
        for call in calls:
            assert len(call[0]) == 1
            assert call[1] == {}

        assert "Signed PSBT" in str(calls[0][0][0])
        assert signed_psbt_b64 in str(calls[1][0][0])
        
        mock_display_data_as_animated_qrs.assert_called_once_with(signed_psbt_b64)
