import hashlib
import math
import zlib
from prompt_toolkit import prompt, print_formatted_text
from typing import List

def self_entropy(input: str) -> float:
    """Measure the self-entropy of a given string

    Models the string as produced by a Markov process.  See
    https://en.wikipedia.org/wiki/Entropy_(information_theory)#Data_as_a_Markov_process

    """
    inputBytes = input.encode('utf8')
    counts = [0]*256
    for byte in inputBytes:
        counts[byte] += 1
    total = len(inputBytes)
    entropy_per_byte = 0.0
    for c in counts:
        if c != 0:
            entropy_per_byte += (c / total) * math.log(total / c, 2)
    return entropy_per_byte * total


def compression_entropy(input: str) -> float:
    """Measure the compression entropy of a given string

    Compresses the string with the zlib algorithm.
    """
    return 8 * len(zlib.compress(input.encode('utf-8'), 9))


def entropy(input: str) -> float:
    """Return the most conservative measure of entropy for the given string

    Returns the minimum of the self-entropy and compression entropy.
    """
    return min(self_entropy(input), compression_entropy(input))


def enter_randomness(chunks: int) -> bytes:
    """Enter a specified amount of random data

    The total number of bits of randomness is equal to `chunks * 256`.

    """
    print_formatted_text(
        "\nEnter at least {} bits worth of random data.\n".
        format(chunks * 256))
    lines: List = []
    input_entropy = 0.0

    output = bytes()

    target = 256

    while True:
        try:
            prompt_msg = (
                "Collected {0:5.1f} bits (Ctrl-D to Stop)"
                .format(input_entropy))
            line = prompt(prompt_msg).strip()
        except EOFError:
            break

        lines += line
        input_entropy = entropy(''.join(lines))

        if input_entropy > target:
            output += hashlib.sha256(''.join(lines).encode('utf-8')).digest()
            target += 256

    return output


class RandomGenerator:
    """An "interactive random number generator"

    Lets the user enter random data, however they are creating it, and
    ensures that the total entropy is sufficient.

    """

    def __init__(self) -> None:
        self.bytes = b''
        self.size = 0
        self.active = True

    def get_more(self, count) -> None:
        chunks = (count + 31) // 32
        more = enter_randomness(chunks)
        self.bytes += more
        self.size += len(more)

    def random(self, size: int) -> bytes:
        while(self.size < size):
            self.get_more(size - self.size)

        out = self.bytes[:size]
        self.bytes = self.bytes[size:]
        self.size -= size
        return out

    def ensure_bytes(self, total):
        if self.active and self.size < total:
            self.get_more(total - self.size)
