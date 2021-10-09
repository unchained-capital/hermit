import hashlib
import math
import zlib
from prompt_toolkit import prompt, print_formatted_text, HTML
from typing import List


def max_entropy_estimate(input: str) -> float:
    """Estimate the entropy of the given string.

    Works conservatively, by choosing the minimum of the self-entropy
    and Kolmogorov entropy.

    """
    return min(max_self_entropy(input), max_kolmogorov_entropy_estimate(input))


def max_self_entropy(input: str) -> float:
    """Measure the maximum self-entropy of a given string (in bits).

    Models the string as produced by a Markov process which means the
    self-entropy has the following properties:

    1) it is proportional to the length of the string
    2) it is independent of the order of the characters in the string
    3) because of (2), it is an upper bound on entropy

    See
    https://en.wikipedia.org/wiki/Entropy_(information_theory)#Data_as_a_Markov_process

    """
    inputBytes = input.encode("utf8")
    counts = [0] * 256
    for byte in inputBytes:
        counts[byte] += 1
    total = len(inputBytes)
    entropy_per_byte = 0.0
    for count in counts:
        # We can ignore counts of zero since they don't contribute
        # any entropy (probability = 0 and the product below
        # vanishes).
        if count != 0:
            probability = float(count) / float(total)
            # Taking the log base 2 is what gets us bits.
            log2_probability = math.log(probability, 2)
            entropy_per_byte += probability * log2_probability
    # Log probabilities are negative, so we return the absolute value
    # of the result.  (We could also have inverted the ratio of the
    # value we took the log_2 base of, but this is easier for most
    # people to understand IMO).
    return abs(entropy_per_byte * total)


def max_kolmogorov_entropy_estimate(input: str) -> float:
    """Estimates the Kolmogorov entropy of the given string (in bits).

    Uses the zlib compression algorithm to estimate the total
    information in the string.

    This is an upper bound because there certainly exist other
    algorithms which could better compress the given string.

    """
    # Multiply by 8 to turn number of bytes into bits.
    return 8 * len(zlib.compress(input.encode("utf8"), 9))


def enter_randomness(chunks: int) -> bytes:
    """Enter a specified amount of random data

    The total number of bits of randomness is equal to `chunks * 256`.

    """
    print_formatted_text(
        HTML(
            """
<b>Enter at least {} bits worth of random data.</b>

Hit <b>CTRL-D</b> when done.
""".format(
                chunks * 256
            )
        )
    )
    lines: List = []
    input_entropy = 0.0

    output = bytes()

    target = 256

    while True:
        try:
            prompt_msg = "Collected {0:5.1f} bits>:".format(input_entropy)
            line = prompt(prompt_msg).strip()
        except EOFError:
            break

        lines += line
        input_entropy = max_entropy_estimate("".join(lines))

        if input_entropy > target:
            output += hashlib.sha256("".join(lines).encode("utf-8")).digest()
            target += 256

    return output


class RandomGenerator:
    """An "interactive random number generator"

    Lets the user enter random data, however they are creating it, and
    ensures that the total entropy is sufficient.

    """

    def __init__(self) -> None:
        self.bytes = b""
        self.size = 0
        self.active = True

    def get_more(self, count) -> None:
        chunks = (count + 31) // 32
        more = enter_randomness(chunks)
        self.bytes += more
        self.size += len(more)

    def random(self, size: int) -> bytes:
        while self.size < size:
            self.get_more(size - self.size)

        out = self.bytes[:size]
        self.bytes = self.bytes[size:]
        self.size -= size
        return out

    def ensure_bytes(self, total):
        if self.active and self.size < total:
            self.get_more(total - self.size)
