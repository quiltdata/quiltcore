from quiltcore import Codec, Verifiable

class Verify(Verifiable):

    TEST_HASH = "1220d04b98f48e8f8bcc15c6ae5ac050801cd6dcfd428fb5f9e65c4e16e7807340fa"

    def __init__(self, **kwargs):
        codec = Codec()
        super().__init__(codec, **kwargs)
        self._hash = self.TEST_HASH

    def to_bytes(self):
        return b"hash"

    def hashable_dict(self):
        return {}

def test_verifiable():
    codec = Codec()
    verifiable = Verifiable(codec)
    assert verifiable is not None

def test_verify():
    verify = Verify()
    assert verify is not None

    assert verify.hash() == Verify.TEST_HASH
    assert verify.q3hash() == Verify.TEST_HASH[4:]
    assert verify.hashable() == b"{}"
    assert verify.verify(b"") == False
    assert verify.verify(b"hash") == True
    assert verify.verify(b"hash2") == False