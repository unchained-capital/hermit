
# This file is substantially copied from the reference implementation for
# slip-0039 -- see https://github.com/satoshilabs/slips/blob/master/slip-0039.md
#
# The two main differences are that it provides a means to encrypt the
# shard data for each shard, and it exposes a mechanism to export
# shards as byte arrays for efficient storage.
#
# What follows is the copyright message from the original file:
#
# Copyright (c) 2018 Andrew R. Kozlik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import hashlib
import hmac
import os

from shamir_mnemonic import *
from shamir_mnemonic import _encrypt, _decrypt, _int_from_indices, _int_to_indices

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
    encrypted_value = _encrypt(value, passphrase, iteration_exponent, identifier)
    return (identifier, iteration_exponent, group_index, group_threshold, groups, member_index, member_threshold, encrypted_value)

def decrypt_shard(passphrase, encrypted_shard):
    (identifier, iteration_exponent, group_index, group_threshold, groups, member_index, member_threshold, encrypted_value) = encrypted_shard
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

