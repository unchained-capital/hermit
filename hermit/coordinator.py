from typing import Tuple

from buidl import PSBT
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .config import get_config
from .errors import InvalidCoordinatorSignature

from buidl import PrivateKey, S256Point, Signature

#: The key that holds an optional coordinator signature for a PSBT.
COORDINATOR_SIGNATURE_KEY: bytes = "coordinator_sig".encode("utf8")


def validate_coordinator_signature_if_necessary(original_psbt: PSBT) -> None:
    """Validates the given PSBT has a valid coordinator signature, if necessary.

    Raises :class:`~hermit.errors.InvalidCoordinatorSignature` if the
    signature is invalid.

    If the PSBT lacks a coordinator signature, and one is required
    (see :attr:`~hermit.config.HermitConfig.DefaultCoordinator`), will again raise
    :class:`~hermit.errors.InvalidCoordinatorSignature`

    If a coordinator signature is not required, PSBTs without one will
    be valid.  PSBTs with coordinator signatures will still have their
    signatures fully-validated in this case.

    Coordinator signatures are RSA signatures verified using a public
    key stored in Hermit's configuration (see
    :attr:`~hermit.config.HermitConfig.DefaultCoordinator`).

    """

    signature_required = get_config().coordinator["signature_required"]
    if COORDINATOR_SIGNATURE_KEY not in original_psbt.extra_map:
        if signature_required:
            raise InvalidCoordinatorSignature("Coordinator signature is missing.")
        else:
            return

    unsigned_psbt_base64_bytes, sig_bytes = extract_rsa_signature_params(original_psbt)
    validate_rsa_signature(unsigned_psbt_base64_bytes, sig_bytes)


def create_secp256k1_signature(message: bytes, private_key_path: str) -> bytes:
    """Create a secp256k1 signature.

    This function is not called within usual Hermit operation. It is useful
    for scripts and tests.
    """
    with open(private_key_path, mode="r") as private_key_file:
        private_key = PrivateKey.parse(private_key_file.read().strip())

    signature = private_key.sign_message(message)
    return signature.der()


def create_rsa_signature(message: bytes, private_key_path: str) -> bytes:
    """Create an RSA signature.

    This function is not called within usual Hermit operation.  It is
    useful for scripts and tests.

    """

    with open(private_key_path, mode="r") as private_key_file:
        private_key = RSA.importKey(private_key_file.read())

    digest = SHA256.new()
    digest.update(message)
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(digest)
    return signature


def validate_rsa_signature(message: bytes, signature: bytes) -> None:
    """Validate an RSA signature.

    Uses the public key from Hermit's configuration for verification
    (see :attr:`~hermit.config.DefaultCoordinator`).

    Will raise :class:`~hermit.errors.InvalidCoordinatorSignature` if
    the public key is missing or invalid or if the signature is
    invalid.

    """
    public_key_text = get_config().coordinator.get("public_key")
    if public_key_text is None:
        raise InvalidCoordinatorSignature(
            "Coordinator signature is present but no public key is configured."
        )

    try:
        public_key = RSA.importKey(public_key_text)
    except Exception:
        raise InvalidCoordinatorSignature(
            "Coordinator signature is present but coordinator public key is invalid."
        )

    digest = SHA256.new()
    digest.update(message)
    verifier = PKCS1_v1_5.new(public_key)
    if not verifier.verify(digest, signature):  # type: ignore
        raise InvalidCoordinatorSignature("Coordinator signature is invalid.")


def validate_secp256k1_signature(message: bytes, signature: bytes) -> None:
    """Validate a secp256k1 signature.

    Uses the public key from Hermit's configuration for verification
    (see :attr:`~hermit.config.DefaultCoordinator`).

    Will raise :class:`~hermit.errors.InvalidCoordinatorSignature` if
    the public key is missing or invalid or if the signature is
    invalid.

    """
    public_key_text = get_config().coordinator.get("public_key")

    if public_key_text is None:
        raise InvalidCoordinatorSignature(
            "Coordinator signature is present but no public key is configured."
        )

    try:
        public_key = S256Point.parse(bytes.fromhex(public_key_text))
    except Exception:
        raise InvalidCoordinatorSignature(
            "Coordinator signature is present but coordinator public key is invalid."
        )

    sig = Signature.parse(signature)

    if not public_key.verify_message(message, sig):
        raise InvalidCoordinatorSignature("Coordinator signature is invalid.")


def extract_rsa_signature_params(original_psbt: PSBT) -> Tuple[bytes, bytes]:
    return extract_signature_params(original_psbt)


def extract_signature_params(original_psbt: PSBT) -> Tuple[bytes, bytes]:
    """Extract signature parameters from a PSBT.

    The value of the :attr:`COORDINATOR_SIGNATURE_KEY` key within the
    PSBT's `extra_map` is extracted as the signature bytes.

    This key is then deleted and the PSBT re-serialized to base 64
    bytes.  This is the message assumed to be signed by the signature
    bytes.

    """

    sig_bytes = original_psbt.extra_map[COORDINATOR_SIGNATURE_KEY]

    # FIXME how do we make a copy of a PSBT object?
    unsigned_psbt = PSBT.parse_base64(original_psbt.serialize_base64())
    del unsigned_psbt.extra_map[COORDINATOR_SIGNATURE_KEY]
    unsigned_psbt_base64 = unsigned_psbt.serialize_base64()
    unsigned_psbt_base64_bytes = unsigned_psbt_base64.encode("utf8")

    return unsigned_psbt_base64_bytes, sig_bytes


def add_rsa_signature(original_psbt: PSBT, private_key_path: str) -> PSBT:
    """Add a signature to a PSBT.

    This is useful for scripts and tests, but not actually ever called in
    the course of regular Hermit operation
    """

    psbt_base64 = original_psbt.serialize_base64()

    sig_bytes = create_rsa_signature(
        bytes(psbt_base64, "utf-8"),
        private_key_path,
    )

    original_psbt.extra_map[COORDINATOR_SIGNATURE_KEY] = sig_bytes
    return original_psbt


def add_secp256k1_signature(original_psbt: PSBT, private_key_path: str) -> PSBT:
    """Add a signature to a PSBT.

    This is useful for scripts and tests, but not actually ever called in
    the course of regular Hermit operation
    """

    psbt_base64 = original_psbt.serialize_base64()

    sig_bytes = create_secp256k1_signature(
        bytes(psbt_base64, "utf-8"),
        private_key_path,
    )

    original_psbt.extra_map[COORDINATOR_SIGNATURE_KEY] = sig_bytes
    return original_psbt
