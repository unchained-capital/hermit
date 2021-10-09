import hashlib
from string import ascii_letters
from random import shuffle
from unittest.mock import patch

import hermit
from hermit.rng import (
    max_self_entropy, 
    max_kolmogorov_entropy_estimate, 
    max_entropy_estimate, 
    enter_randomness,
)

def test_max_self_entropy():
    # An empty string should have zero self entropy.
    empty_string_entropy = max_self_entropy("")
    assert empty_string_entropy == 0

    # A repeated character string should have zero self entropy.
    single_character_entropy = max_self_entropy("a" * 256)
    assert single_character_entropy == 0

    # A string of N unique characters should have self entropy > N.
    alphabet = ascii_letters[:]
    alphabet_entropy = max_self_entropy(alphabet)
    assert alphabet_entropy > 256

    # A shuffled string of N unique characters should have self
    # entropy == to the original string.
    shuffled_alphabet_list = list(alphabet)
    shuffle(shuffled_alphabet_list)
    shuffled_alphabet = ''.join(shuffled_alphabet_list)
    shuffled_alphabet_entropy = max_self_entropy(shuffled_alphabet)
    assert shuffled_alphabet_entropy == alphabet_entropy

    # Doubling a string of characters just doubles the self entropy.
    double_alphabet = alphabet + alphabet
    double_alphabet_entropy = max_self_entropy(double_alphabet)
    assert double_alphabet_entropy == 2 * alphabet_entropy


def test_max_kolmogorov_entropy_estimate():
    # An empty string has some size after compression.
    empty_string_entropy = max_kolmogorov_entropy_estimate("")
    assert empty_string_entropy == 64

    # A repeated character string has some size after compression.
    single_character_entropy = max_kolmogorov_entropy_estimate("a" * 256)
    assert single_character_entropy == 96

    # A string of N unique characters has size > N after compression.
    alphabet = ascii_letters[:]
    alphabet_entropy = max_kolmogorov_entropy_estimate(alphabet)
    assert alphabet_entropy > 256

    # A shuffled string of N unique characters should compress to the
    # same value as the original string because there are no
    # interesting bigrams.
    shuffled_alphabet_list = list(alphabet)
    shuffle(shuffled_alphabet_list)
    shuffled_alphabet = ''.join(shuffled_alphabet_list)
    shuffled_alphabet_entropy = max_kolmogorov_entropy_estimate(shuffled_alphabet)
    assert shuffled_alphabet_entropy == alphabet_entropy

    # Doublig a string of characters should less than double the
    # compression output.
    double_alphabet = alphabet + alphabet
    double_alphabet_entropy = max_kolmogorov_entropy_estimate(double_alphabet)
    assert alphabet_entropy < double_alphabet_entropy < 2 * alphabet_entropy

@patch("hermit.rng.max_self_entropy")
@patch("hermit.rng.max_kolmogorov_entropy_estimate")
class TestMaxEntropyEstimate(object):

    def setup(self):
        self.input = "foobar"
        
    def test_self_entropy_exceeds_kolmogorov_entropy(self, mock_max_kolmogorov_entropy_estimate, mock_max_self_entropy):
        mock_max_kolmogorov_entropy_estimate.return_value = 10
        mock_max_self_entropy.return_value = 100
        assert max_entropy_estimate(self.input) == 10
        assert mock_max_kolmogorov_entropy_estimate.called_once_with(self.input)
        assert mock_max_self_entropy.called_once_with(self.input)

    def test_kolmogorov_entropy_exceeds_self_entropy(self, mock_max_kolmogorov_entropy_estimate, mock_max_self_entropy):
        mock_max_kolmogorov_entropy_estimate.return_value = 100
        mock_max_self_entropy.return_value = 10
        assert max_entropy_estimate(self.input) == 10
        assert mock_max_kolmogorov_entropy_estimate.called_once_with(self.input)
        assert mock_max_self_entropy.called_once_with(self.input)

    def test_kolmogorov_entropy_equals_self_entropy(self, mock_max_kolmogorov_entropy_estimate, mock_max_self_entropy):
        mock_max_kolmogorov_entropy_estimate.return_value = 10
        mock_max_self_entropy.return_value = 10
        assert max_entropy_estimate(self.input) == 10
        assert mock_max_kolmogorov_entropy_estimate.called_once_with(self.input)
        assert mock_max_self_entropy.called_once_with(self.input)

@patch("hermit.rng.prompt")
def test_enter_randomness(mock_prompt):
    mock_prompt.side_effect = [
        "foo\n",
        "bar\n",
        ascii_letters + "\n",
        EOFError()
    ]
    data = enter_randomness(1)
    assert data == hashlib.sha256(("foobar" + ascii_letters).encode("utf8")).digest()
    prompt_calls = mock_prompt.call_args_list
    assert len(prompt_calls) == 4

    for call in prompt_calls:
        assert len(call[0]) == 1
        assert call[1] == {}

    assert "0.0 bits" in prompt_calls[0][0][0]
    assert "2.8 bits" in prompt_calls[1][0][0]
    assert "13.5 bits" in prompt_calls[2][0][0]
    assert "327.0 bits" in prompt_calls[3][0][0]
