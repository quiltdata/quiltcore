from pytest import fixture
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
    manifest = reg.get(TEST_HASH)
    assert isinstance(manifest, CoreName)


def test_name_get(reg):
    first = reg.list()[0]
    man = first.get(TEST_TAG)
    assert TEST_HASH in str(man)

    latest = first.get("latest")
    assert isinstance(latest, CoreManifest)
