
# This file was originally substantially copied from the reference implementation for
# slip-0039, now it imports that functionality from the pypi mosule shamir_mnemonic.
#
# The two main differences are that it provides a means to encrypt the
# shard data for each shard, and it exposes a mechanism to export
# shards as byte arrays for efficient storage. 
#
#

import hashlib
import hmac
import os

import shamir_mnemonic
from shamir_mnemonic import *
from shamir_mnemonic import _encrypt, _decrypt, _int_from_indices, _int_to_indices

# shamir_mnemonic expects us to update its local copy of RANDOM_BYTES in order
# to override the random number generator. Instead of exposing this complication
# to the rest of the hermit code, we expose setting the global random number
# generator as set_random_bytes.

old_rngs = []
def set_random_bytes(rng):
    old_rngs.append(shamir_mnemonic.RANDOM_BYTES)
    shamir_mnemonic.RANDOM_BYTES = rng

def restore_random_bytes():
    if(length(old_rngs)>0):
        shamir_mnemonic.RANDOM_BYTES = old_rngs.pop()

def mnemonic_from_bytes(bytes_data):
    """
    Converts a 32-byte array into mnemonics.
    """
    return mnemonic_from_indices(_int_to_indices(int.from_bytes(bytes_data,'big'), (8*len(bytes_data)) // RADIX_BITS, RADIX_BITS))


def mnemonic_to_bytes(mnemonic):
    """
    Converts a mnemonic into a 32-byte array.
    """
    wordlength = len(mnemonic.split(' '))
    return _int_from_indices(mnemonic_to_indices(mnemonic)).to_bytes(bits_to_bytes(RADIX_BITS*wordlength) ,'big')

def encrypt_shard(passphrase, unencrypted_shard):
    (identifier, iteration_exponent, group_index, group_threshold, groups, member_index, member_threshold, value) = unencrypted_shard
    encrypted_value = value
    # If there was not passphrase given, do not actually encrypt anything
    if passphrase is not None:
        encrypted_value = _encrypt(value, passphrase, iteration_exponent, identifier)
    return (identifier, iteration_exponent, group_index, group_threshold, groups, member_index, member_threshold, encrypted_value)

def decrypt_shard(passphrase, encrypted_shard):
    (identifier, iteration_exponent, group_index, group_threshold, groups, member_index, member_threshold, encrypted_value) = encrypted_shard
    decrypted_value = encrypted_value
    # If not passphrase was given, do not actually decrypt anything
    if passphrase is not None:
        decrypted_value = _decrypt(encrypted_value, passphrase, iteration_exponent, identifier)
    return (identifier, iteration_exponent, group_index, group_threshold, groups, member_index, member_threshold, decrypted_value)

def decrypt_mnemonic(mnemonic, passphrase):
    decoded = decode_mnemonic(mnemonic)
    decrypted = decrypt_shard(passphrase, decoded)
    return encode_mnemonic(*decrypted)

def reencrypt_mnemonic(mnemonic, oldpassphrase, newpassphrase):
    decoded = decode_mnemonic(mnemonic)
    decrypted = decrypt_shard(oldpassphrase, decoded)
    encrypted = encrypt_shard(newpassphrase, decrypted)
    return encode_mnemonic(*encrypted)

def encrypt_mnemonic(mnemonic, passphrase):
    decoded = decode_mnemonic(mnemonic)
    encrypted = encrypt_shard(passphrase, decoded)
    return encode_mnemonic(*encrypted)

