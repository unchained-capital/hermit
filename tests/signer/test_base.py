from prompt_toolkit import prompt, PromptSession, HTML, print_formatted_text
from unittest.mock import patch, create_autospec
import json
import pytest

import hermit
from hermit.signer import Signer
from hermit.wallet import HDWallet


class FakeShards:
    def __init__(self, words):
        self.words = words

    def wallet_words(self):
        return self.words


@patch("hermit.signer.reader.read_qr_code")
class TestSignerValidates(object):
    @pytest.fixture(autouse=True)
    def setup_wallet_and_request(
        self, bitcoin_testnet_signature_request, opensource_wallet_words
    ):
        self.wallet = HDWallet()
        self.wallet.shards = FakeShards(opensource_wallet_words)
        self.request = json.loads(bitcoin_testnet_signature_request)

    #
    # Request
    #
    def test_invalid_json_is_error(self, mock_request):
        mock_request.return_value = "this is not json"
        with pytest.raises(hermit.errors.HermitError) as e_info:
            Signer(self.wallet).sign(testnet=True)
        print(e_info)
        err_msg = "Expecting value: line 1 column 1 (char 0) (JSONDecodeError)"
        assert str(e_info.value) == "Invalid signature request: " + err_msg

    #
    # BIP32 Path
    #

    def test_BIP32_path_not_string_is_error(self, mock_request):
        bip32_path = [""]
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = 123
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = True
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = {"a": 123, "b": 456}
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = None
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        expected = "Invalid signature request: " + "BIP32 path must be a string."
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected

    def test_invalid_BIP32_paths_raise_error(self, mock_request):
        bip32_path = "m/123/"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = "123'/1234/12"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = "m"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info3:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = "m123/123'/123/43"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info4:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = "m/123'/12''/12/123"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info5:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = "m/123'/12'/-12/123"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info6:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        expected = "Invalid signature request: " + "invalid BIP32 path formatting."
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected
        assert str(e_info3.value) == expected
        assert str(e_info4.value) == expected
        assert str(e_info5.value) == expected
        assert str(e_info6.value) == expected

    def test_BIP32_node_too_high_raises_error(self, mock_request):
        bip32_path = "m/0'/0'/2147483648/0"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info1:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        bip32_path = "m/0'/0'/2147483648'/0"
        mock_request.return_value = json.dumps(self.request)
        with pytest.raises(hermit.errors.InvalidSignatureRequest) as e_info2:
            Signer(self.wallet).validate_bip32_path(bip32_path)

        expected = "Invalid signature request: " + "invalid BIP32 path."
        assert str(e_info1.value) == expected
        assert str(e_info2.value) == expected


@patch("hermit.signer.reader.read_qr_code")
@patch("hermit.signer.displayer.display_qr_code")
@patch("hermit.signer.base.input")
class TestSigner(object):
    @pytest.fixture(autouse=True)
    def setup_wallet_and_request(
        self, bitcoin_testnet_signature_request, opensource_wallet_words
    ):
        self.wallet = HDWallet()
        self.wallet.shards = FakeShards(opensource_wallet_words)
        self.request = json.loads(bitcoin_testnet_signature_request)

    def test_confirm_signature_prompt(
        self, mock_input, mock_display_qr_code, mock_request
    ):
        mock_input.return_value = "y"
        mock_request.return_value = json.dumps(self.request)
        Signer(self.wallet).sign(testnet=True)
        input_prompt = "Sign the above transaction? [y/N] "
        mock_input.assert_called_with(input_prompt)

    def test_confirm_signature_prompt_in_session(
        self, mock_input, mock_display_qr_code, mock_request
    ):
        mock_session = create_autospec(PromptSession)
        mock_session.prompt.return_value = "y"
        mock_request.return_value = json.dumps(self.request)
        Signer(self.wallet, mock_session).sign(testnet=True)
        input_prompt = "Sign the above transaction? [y/N] "
        assert input_prompt in mock_session.prompt.call_args[0][0].value

    @patch("hermit.signer.Signer._parse_request")
    def test_no_request_returned(
        self, mock_parse_request, mock_input, mock_display_qr_code, mock_request
    ):
        mock_request.return_value = None
        Signer(self.wallet).sign(testnet=True)
        assert not mock_parse_request.called

    def test_no_request_raises_error_parse_request(
        self, mock_parse_request, mock_input, mock_display_qr_code
    ):
        with pytest.raises(hermit.errors.HermitError) as e_info:
            Signer(self.wallet)._parse_request()
        err_msg = "No Request Data"
        assert str(e_info.value) == err_msg

    @patch("hermit.signer.Signer.create_signature")
    def test_decline_signature_prompt(
        self, mock_create_signature, mock_input, mock_display_qr_code, mock_request
    ):
        mock_input.return_value = "N"
        mock_request.return_value = json.dumps(self.request)
        Signer(self.wallet).sign(testnet=True)
        assert not mock_create_signature.called
