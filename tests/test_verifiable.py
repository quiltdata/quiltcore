from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import fixture, raises

from quiltcore import Codec, Verifiable


@fixture
def ver():
    return Verifiable(Codec())


class Verify(Verifiable):
    TEST_BYTES = b"hash"
    HASH_BYTES = "1220d04b98f48e8f8bcc15c6ae5ac050801cd6dcfd428fb5f9e65c4e16e7807340fa"
    HASH_HASH = "12209577cb12add200bb6c6059d5ff459c69beeb8b5a80845ad17ae80a17276af024"
    TEST_DICT = {"hash": "hash"}
    HASH_DICT = "1220441b04ecf9bcccf1129dc609bf94e0fca64a79c6ebc7012168ff432384d7f880"

    def __init__(self, **kwargs):
        codec = Codec()
        super().__init__(codec, **kwargs)

    def to_bytes(self):
        return self.TEST_BYTES


def test_ver(ver: Verifiable):
    assert ver is not None


def test_ver_raise(ver: Verifiable):
    with raises(ValueError):
        ver.to_bytes()
    with raises(ValueError):
        ver.hashify()


def test_ver_dict(ver: Verifiable):
    OLD_DICT = Verifiable.DEFAULT_DICT
    Verifiable.DEFAULT_DICT = Verify.TEST_DICT
    assert ver.hashify() == Verify.HASH_DICT
    Verifiable.DEFAULT_DICT = OLD_DICT


def test_ver_cache(ver: Verifiable):
    ver["hash"] = Verify()
    assert ver.to_bytes() == Verify.HASH_BYTES.encode("utf-8")
    assert ver.hashify() == Verify.HASH_HASH


def test_ver_path(ver: Verifiable):
    with TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / "test.txt"
        path.write_bytes(Verify.TEST_BYTES)
        ver.path = path  # type: ignore
        assert ver.hashify() == Verify.HASH_BYTES


def test_verify():
    verify = Verify()
    assert verify is not None

    assert verify.hashify() == Verify.HASH_BYTES
    assert verify.q3hash() == Verify.HASH_BYTES[4:]
    assert verify.hashable() == b"{}"
    assert verify.verify(b"") is False
    assert verify.verify(b"hash") is True
    assert verify.verify(b"hash2") is False
