from unittest.mock import Mock, patch
from pytest import raises

from hermit import InvalidCoordinatorSignature
from hermit.coordinator import (
    validate_coordinator_signature_if_necessary,
    validate_rsa_signature,
    extract_rsa_signature_params,
    create_rsa_signature,
    COORDINATOR_SIGNATURE_KEY,
)


@patch("hermit.coordinator.get_config")
class TestValidateCoordinatorSignatureIfNecessary(object):
    def setup(self):
        self.psbt = Mock()
        self.extra_map = dict()
        self.psbt.extra_map = self.extra_map

        self.config = Mock()
        self.coordinator_config = dict()
        self.config.coordinator = self.coordinator_config

        self.message = Mock()
        self.signature = Mock()

    def test_signature_absent_and_not_required(self, mock_get_config):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = False
        assert validate_coordinator_signature_if_necessary(self.psbt) is True
        mock_get_config.assert_called_once_with()

    def test_when_signature_absent_and_required(self, mock_get_config):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = True
        with raises(InvalidCoordinatorSignature) as e:
            validate_coordinator_signature_if_necessary(self.psbt) is False
        assert "signature is missing" in str(e)
        mock_get_config.assert_called_once_with()

    @patch("hermit.coordinator.extract_rsa_signature_params")
    @patch("hermit.coordinator.validate_rsa_signature")
    def test_when_signature_valid_and_not_required(
        self,
        mock_validate_rsa_signature,
        mock_extract_rsa_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = False

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_rsa_signature_params.return_value = (self.message, self.signature)

        mock_validate_rsa_signature.return_value = True

        assert validate_coordinator_signature_if_necessary(self.psbt) is True
        mock_get_config.assert_called_once_with()
        mock_extract_rsa_signature_params.assert_called_once_with(self.psbt)
        mock_validate_rsa_signature.assert_called_once_with(
            self.message, self.signature
        )

    @patch("hermit.coordinator.extract_rsa_signature_params")
    @patch("hermit.coordinator.validate_rsa_signature")
    def test_when_signature_valid_and_required(
        self,
        mock_validate_rsa_signature,
        mock_extract_rsa_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = True

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_rsa_signature_params.return_value = (self.message, self.signature)

        mock_validate_rsa_signature.return_value = True

        assert validate_coordinator_signature_if_necessary(self.psbt) is True
        mock_get_config.assert_called_once_with()
        mock_extract_rsa_signature_params.assert_called_once_with(self.psbt)
        mock_validate_rsa_signature.assert_called_once_with(
            self.message, self.signature
        )

    @patch("hermit.coordinator.extract_rsa_signature_params")
    @patch("hermit.coordinator.validate_rsa_signature")
    def test_when_signature_invalid_and_not_required(
        self,
        mock_validate_rsa_signature,
        mock_extract_rsa_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = False

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_rsa_signature_params.return_value = (self.message, self.signature)

        mock_validate_rsa_signature.return_value = False

        assert validate_coordinator_signature_if_necessary(self.psbt) is False
        mock_get_config.assert_called_once_with()
        mock_extract_rsa_signature_params.assert_called_once_with(self.psbt)
        mock_validate_rsa_signature.assert_called_once_with(
            self.message, self.signature
        )

    @patch("hermit.coordinator.extract_rsa_signature_params")
    @patch("hermit.coordinator.validate_rsa_signature")
    def test_when_signature_invalid_and_required(
        self,
        mock_validate_rsa_signature,
        mock_extract_rsa_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = True

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_rsa_signature_params.return_value = (self.message, self.signature)

        mock_validate_rsa_signature.return_value = False

        assert validate_coordinator_signature_if_necessary(self.psbt) is False
        mock_get_config.assert_called_once_with()
        mock_extract_rsa_signature_params.assert_called_once_with(self.psbt)
        mock_validate_rsa_signature.assert_called_once_with(
            self.message, self.signature
        )


@patch("hermit.coordinator.get_config")
def test_create_rsa_sigature(mock_get_config):
    public_key = open("tests/fixtures/coordinator.pub", "r").read()
    private_key_path = "tests/fixtures/coordinator.pem"

    message = "Hello there".encode("utf8")
    signature = create_rsa_signature(message, private_key_path)

    config = Mock()
    coordinator_config = dict(public_key=public_key)
    config.coordinator = coordinator_config
    mock_get_config.return_value = config
    assert validate_rsa_signature(message, signature) is True
    mock_get_config.assert_called_once_with()


@patch("hermit.coordinator.get_config")
class TestValidateRSASignature(object):
    def setup(self):
        self.public_key = open("tests/fixtures/coordinator.pub", "r").read()
        self.private_key_path = "tests/fixtures/coordinator.pem"

        self.message = "Hello there".encode("utf8")
        self.signature = create_rsa_signature(self.message, self.private_key_path)

        self.config = Mock()
        self.coordinator_config = dict(public_key=self.public_key)
        self.config.coordinator = self.coordinator_config

    def test_when_signature_is_valid(self, mock_config):
        mock_config.return_value = self.config
        assert validate_rsa_signature(self.message, self.signature) is True
        mock_config.assert_called_once_with()

    def test_when_signature_is_invalid(self, mock_config):
        mock_config.return_value = self.config
        with raises(InvalidCoordinatorSignature) as e:
            validate_rsa_signature(self.message + b"hello", self.signature)
        mock_config.assert_called_once_with()
        assert "signature is invalid" in str(e)
