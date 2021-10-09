from typing import Optional

from buidl import PSBT
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

from .config import get_config
from .errors import InvalidCoordinatorSignature

#: The key that holds an optional coordinator signature for a PSBT.
COORDINATOR_SIGNATURE_KEY = "coordinator_sig".encode("utf8")


def validate_coordinator_signature_if_necessary(original_psbt: PSBT) -> Optional[bool]:
    signature_required = get_config().coordinator["signature_required"]
    if COORDINATOR_SIGNATURE_KEY not in original_psbt.extra_map:
        if signature_required:
            raise InvalidCoordinatorSignature("Coordinator signature is missing.")
        else:
            return True

    unsigned_psbt_base64_bytes, sig_bytes = extract_rsa_signature_params(original_psbt)
    return validate_rsa_signature(unsigned_psbt_base64_bytes, sig_bytes)


def create_rsa_signature(message: bytes, private_key_path: str) -> bytes:
    with open(private_key_path, mode="r") as private_key_file:
        private_key = RSA.importKey(private_key_file.read())

    digest = SHA256.new()
    digest.update(message)
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(digest)
    return signature


def validate_rsa_signature(message: bytes, signature: bytes) -> Optional[bool]:
    public_key_text = get_config().coordinator["public_key"]
    if public_key_text is None:
        raise InvalidCoordinatorSignature(
            "Coordinator signature is present but no public key is configured."
        )

    public_key = RSA.importKey(public_key_text)

    digest = SHA256.new()
    digest.update(message)
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(digest, signature)
    if not verified:
        raise InvalidCoordinatorSignature("Coordinator signature is invalid.")
    return True


def extract_rsa_signature_params(original_psbt: PSBT) -> (bytes, bytes):
    sig_bytes = original_psbt.extra_map[COORDINATOR_SIGNATURE_KEY]

    # FIXME how do we make a copy of a PSBT object?
    unsigned_psbt = PSBT.parse_base64(original_psbt.serialize_base64())
    del unsigned_psbt.extra_map[COORDINATOR_SIGNATURE_KEY]
    unsigned_psbt_base64 = unsigned_psbt.serialize_base64()
    unsigned_psbt_base64_bytes = unsigned_psbt_base64.encode("utf8")

    return unsigned_psbt_base64_bytes, sig_bytes
