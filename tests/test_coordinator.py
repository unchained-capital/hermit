from unittest.mock import Mock, patch
from pytest import raises
from buidl import PSBT

from hermit import InvalidCoordinatorSignature
from hermit.coordinator import (
    validate_coordinator_signature_if_necessary,
    extract_signature_params,
    create_secp256k1_signature,
    add_secp256k1_signature,
    validate_secp256k1_signature,
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
        validate_coordinator_signature_if_necessary(self.psbt)
        mock_get_config.assert_called_once_with()

    def test_when_signature_absent_and_required(self, mock_get_config):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = True
        with raises(InvalidCoordinatorSignature) as e:
            validate_coordinator_signature_if_necessary(self.psbt)
        assert "signature is missing" in str(e)
        mock_get_config.assert_called_once_with()

    @patch("hermit.coordinator.extract_signature_params")
    @patch("hermit.coordinator.validate_secp256k1_signature")
    def test_when_signature_valid_and_not_required(
        self,
        mock_validate_secp256k1_signature,
        mock_extract_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = False

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_signature_params.return_value = (self.message, self.signature)

        validate_coordinator_signature_if_necessary(self.psbt)
        mock_get_config.assert_called_once_with()
        mock_extract_signature_params.assert_called_once_with(self.psbt)
        mock_validate_secp256k1_signature.assert_called_once_with(
            self.message, self.signature
        )

    @patch("hermit.coordinator.extract_signature_params")
    @patch("hermit.coordinator.validate_secp256k1_signature")
    def test_when_signature_valid_and_required(
        self,
        mock_validate_secp256k1_signature,
        mock_extract_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = True

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_signature_params.return_value = (self.message, self.signature)

        validate_coordinator_signature_if_necessary(self.psbt)
        mock_get_config.assert_called_once_with()
        mock_extract_signature_params.assert_called_once_with(self.psbt)
        mock_validate_secp256k1_signature.assert_called_once_with(
            self.message, self.signature
        )

    @patch("hermit.coordinator.extract_signature_params")
    @patch("hermit.coordinator.validate_secp256k1_signature")
    def test_when_signature_invalid_and_not_required(
        self,
        mock_validate_secp256k1_signature,
        mock_extract_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = False

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_signature_params.return_value = (self.message, self.signature)

        mock_validate_secp256k1_signature.side_effect = InvalidCoordinatorSignature(
            "Invalid signature."
        )

        with raises(InvalidCoordinatorSignature) as e:
            validate_coordinator_signature_if_necessary(self.psbt)

        assert "Invalid signature" in str(e)
        mock_get_config.assert_called_once_with()
        mock_extract_signature_params.assert_called_once_with(self.psbt)
        mock_validate_secp256k1_signature.assert_called_once_with(
            self.message, self.signature
        )

    @patch("hermit.coordinator.extract_signature_params")
    @patch("hermit.coordinator.validate_secp256k1_signature")
    def test_when_signature_invalid_and_required(
        self,
        mock_validate_secp256k1_signature,
        mock_extract_signature_params,
        mock_get_config,
    ):
        mock_get_config.return_value = self.config
        self.coordinator_config["signature_required"] = True

        self.extra_map[COORDINATOR_SIGNATURE_KEY] = self.signature

        mock_extract_signature_params.return_value = (self.message, self.signature)

        mock_validate_secp256k1_signature.side_effect = InvalidCoordinatorSignature(
            "Invalid signature."
        )

        with raises(InvalidCoordinatorSignature) as e:
            validate_coordinator_signature_if_necessary(self.psbt)

        assert "Invalid signature" in str(e)
        mock_get_config.assert_called_once_with()
        mock_extract_signature_params.assert_called_once_with(self.psbt)
        mock_validate_secp256k1_signature.assert_called_once_with(
            self.message, self.signature
        )


@patch("hermit.coordinator.get_config")
def test_create_secp256k1_sigature(mock_get_config):
    public_key = open("tests/fixtures/coordinator.pubkey", "r").read().strip()
    private_key_path = "tests/fixtures/coordinator.privkey"

    message = "Hello there".encode("utf8")
    signature = create_secp256k1_signature(message, private_key_path)

    config = Mock()
    coordinator_config = dict(public_key=public_key)
    config.coordinator = coordinator_config
    mock_get_config.return_value = config
    validate_secp256k1_signature(message, signature)
    mock_get_config.assert_called_once_with()


@patch("hermit.coordinator.get_config")
class TestValidateSECP256K1Signature(object):
    def setup(self):
        self.public_key = open("tests/fixtures/coordinator.pubkey", "r").read().strip()
        self.private_key_path = "tests/fixtures/coordinator.privkey"

        self.message = "Hello there".encode("utf8")
        self.signature = create_secp256k1_signature(self.message, self.private_key_path)

        self.config = Mock()
        self.coordinator_config = dict(public_key=self.public_key)
        self.config.coordinator = self.coordinator_config

    def test_when_no_coordinator_public_key_is_configured(self, mock_config):
        del self.coordinator_config["public_key"]
        mock_config.return_value = self.config
        with raises(InvalidCoordinatorSignature) as e:
            validate_secp256k1_signature(self.message, self.signature)
        assert "no public key is configured" in str(e)
        mock_config.assert_called_once_with()

    def test_when_invalid_coordinator_public_key_is_configured(self, mock_config):
        self.coordinator_config["public_key"] = "foobar"
        mock_config.return_value = self.config
        with raises(InvalidCoordinatorSignature) as e:
            validate_secp256k1_signature(self.message, self.signature)
        assert "public key is invalid" in str(e)
        mock_config.assert_called_once_with()

    def test_when_signature_is_valid(self, mock_config):
        mock_config.return_value = self.config
        validate_secp256k1_signature(self.message, self.signature)
        mock_config.assert_called_once_with()

    def test_when_signature_is_invalid(self, mock_config):
        mock_config.return_value = self.config
        with raises(InvalidCoordinatorSignature) as e:
            validate_secp256k1_signature(self.message + b"hello", self.signature)
        mock_config.assert_called_once_with()
        assert "signature is invalid" in str(e)


# @patch("hermit.coordinator.get_config")
# class TestPSBTSignatureBasics(object):
# def setup(self):
# self.public_key = open("tests/fixtures/coordinator.pub", "r").read()
# self.private_key_path = "tests/fixtures/coordinator.pem"
#
# self.original_psbt_base64 = open(
# "tests/fixtures/signature_requests/2-of-2.p2sh.testnet.psbt", "r"
# ).read()
#
# self.psbt = PSBT.parse_base64(self.original_psbt_base64)
# self.psbt_base64 = self.psbt.serialize_base64()
#
# self.config = Mock()
# self.coordinator_config = dict(public_key=self.public_key)
# self.config.coordinator = self.coordinator_config
#
# def test_psbt_serialization_stable(self, mock_config):
# mock_config.return_value = self.config
#
# p2 = PSBT.parse_base64(self.psbt_base64)
# assert p2.serialize_base64() == self.psbt.serialize_base64()
#
# def test_psbt_signature(self, mock_config):
# mock_config.return_value = self.config
#
# signature = create_rsa_signature(
# bytes(self.psbt_base64, "utf-8"), self.private_key_path
# )
# add_rsa_signature(self.psbt, self.private_key_path)
#
# assert self.psbt.extra_map[COORDINATOR_SIGNATURE_KEY] == signature
#
# def test_validate_psbt_signature(self, mock_config):
# mock_config.return_value = self.config
#
# add_rsa_signature(self.psbt, self.private_key_path)
#
# unsigned_psbt_base64_bytes, sig_bytes = extract_rsa_signature_params(self.psbt)
# validate_rsa_signature(unsigned_psbt_base64_bytes, sig_bytes)


@patch("hermit.coordinator.get_config")
class TestPSBTSignatureSecP256K1Basics(object):
    def setup(self):
        # Pubkey stored in hex in the fixtures folder
        self.public_key = open("tests/fixtures/coordinator.pubkey", "r").read().strip()

        # Privkey stored in wif format in the fixtures folder
        self.private_key_path = "tests/fixtures/coordinator.privkey"
        # self.private_key = PrivateKey.parse(open(self.private_key_path, "r").read().strip())

        self.original_psbt_base64 = open(
            "tests/fixtures/signature_requests/2-of-2.p2sh.testnet.psbt", "r"
        ).read()

        self.psbt = PSBT.parse_base64(self.original_psbt_base64)
        self.psbt_base64 = self.psbt.serialize_base64()

        self.config = Mock()
        self.coordinator_config = dict(public_key=self.public_key)
        self.config.coordinator = self.coordinator_config

    def test_psbt_serialization_stable(self, mock_config):
        mock_config.return_value = self.config

        p2 = PSBT.parse_base64(self.psbt_base64)
        assert p2.serialize_base64() == self.psbt.serialize_base64()

    def test_psbt_signature(self, mock_config):
        mock_config.return_value = self.config

        signature = create_secp256k1_signature(
            bytes(self.psbt_base64, "utf-8"), self.private_key_path
        )

        add_secp256k1_signature(self.psbt, self.private_key_path)

        assert self.psbt.extra_map[COORDINATOR_SIGNATURE_KEY] == signature

    def test_validate_psbt_signature(self, mock_config):
        mock_config.return_value = self.config

        add_secp256k1_signature(self.psbt, self.private_key_path)

        unsigned_psbt_base64_bytes, sig_bytes = extract_signature_params(self.psbt)
        validate_secp256k1_signature(unsigned_psbt_base64_bytes, sig_bytes)
