import string

from hermit.rng import self_entropy, compression_entropy, entropy

class TestSelfEntropy(object):

    # TODO: How to test selfEntropy?
    def test_self_entropy(self):
        some_entropy = self_entropy(string.ascii_letters)
        assert some_entropy > 256
        
        no_entropy = self_entropy('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        assert no_entropy == 0

class TestCompressionEntropy(object):

    # TODO: How to test compressionEntropy?
    def test_compression_entropy(self):
        some_entropy = compression_entropy(string.ascii_letters)
        assert some_entropy > 256
        
        no_entropy = compression_entropy('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        # TODO: ?
        assert no_entropy == 88


class TestEntropy(object):

    # TODO: How to test compressionEntropy?
    def test_compression_entropy(self):
        se = self_entropy(string.ascii_letters)        
        ce = compression_entropy(string.ascii_letters)
        some_entropy = entropy(string.ascii_letters)
        assert some_entropy == min(se, ce)
        
        no_entropy = entropy('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        assert no_entropy == 0
