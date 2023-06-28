from pytest import fixture, raises
from quiltcore import CoreManifest, CoreName, CoreRegistry
from upath import UPath

from .conftest import TEST_BKT, TEST_HASH, TEST_PKG, TEST_TAG


@fixture
def reg():
    path_bkt = UPath(TEST_BKT)
    return CoreRegistry(path_bkt)


def test_registry(reg):
    assert reg
    assert reg.config
    assert ".quilt/named_packages" in str(reg.path)
    assert ".quilt/packages" in str(reg.values)
    assert reg.values.path.exists()
    assert reg.path.is_dir()


def test_registry_list(reg):
    result = reg.list()
    assert isinstance(result, list)
    assert len(result) > 0
    first = result[0]
    assert isinstance(first, CoreName)
    assert TEST_PKG in str(first)


def test_registry_get(reg):
    name = reg.get(TEST_PKG)
    assert isinstance(name, CoreName)
    assert TEST_PKG in str(name)

    with raises(KeyError):
        reg.get("invalid")


def test_name_get(reg):
    name = reg.get(TEST_PKG)
    man = name.get(TEST_TAG)
    assert isinstance(man, CoreManifest)
    assert TEST_HASH in str(man)

    latest = name.get("latest")
    assert isinstance(latest, CoreManifest)
