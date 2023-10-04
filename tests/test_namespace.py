from pytest import fixture
from quiltcore import Manifest, Namespace, Registry

from .conftest import TEST_HASH, TEST_PKG, TEST_TAG, TEST_VOL


@fixture
def reg():
    path_bkt = Manifest.AsPath(TEST_VOL)
    return Registry(path_bkt)


@fixture
def names(reg):
    return reg.getResource(TEST_PKG)


def test_names(names: Namespace):
    assert isinstance(names, Namespace)
    assert "registry" in names.args
    assert names.KEY_NS in names.args.keys()
    assert names.args[names.KEY_NS] == TEST_PKG


def test_names_latest(names: Namespace):
    latest = names.getResource("latest")
    assert isinstance(latest, Manifest)
    assert latest.hash_quilt3() == TEST_HASH


def test_names_man(names: Namespace):
    man = names.getResource(TEST_TAG)
    assert isinstance(man, Manifest)
    assert man.hash_quilt3() == TEST_HASH
    assert TEST_HASH in str(man)
    assert "registry" in man.args
    assert "namespace" in man.args
    assert names.KEY_NS in man.args


def test_names_hash(names: Namespace):
    """use explicit hash, or partial, if provided"""
    latest: Manifest = names.getResource("latest")  # type: ignore
    opts = {names.KEY_HSH: TEST_HASH}
    not_latest: Manifest = names.getResource("latest", **opts)  # type: ignore
    assert latest.hash_quilt3() == not_latest.hash_quilt3()
    assert TEST_HASH == not_latest.hash_quilt3()
    assert names.KEY_HSH == "hash"


def test_names_hash_part(names: Namespace):
    """use explicit hash, or partial, if provided"""
    assert len(TEST_HASH) == names.HASH_LEN
    opts = {names.KEY_HSH: TEST_HASH[:8]}
    not_latest: Manifest = names.getResource("latest", **opts)  # type: ignore
    assert TEST_HASH == not_latest.hash_quilt3()
