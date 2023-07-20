from pytest import fixture, raises
from quiltcore import Manifest, Namespace, Registry
from upath import UPath

from .conftest import TEST_HASH, TEST_PKG, TEST_TAG, TEST_VOL


@fixture
def reg():
    path_bkt = UPath(TEST_VOL)
    return Registry(path_bkt)


def test_reg(reg):
    assert reg
    assert reg.cf
    assert ".quilt/named_packages" in str(reg.path)
    assert ".quilt/packages" in str(reg.manifests)
    assert reg.manifests.exists()
    assert reg.path.is_dir()
    assert "registry" in reg.args


def test_reg_eq(reg):
    path = UPath(TEST_VOL)
    reg2 = Registry(path)
    assert reg == reg2
    assert reg == reg.args["registry"]


def test_reg_list(reg):
    result = reg.list()
    assert isinstance(result, list)
    assert len(result) > 0
    first = result[0]
    assert isinstance(first, Namespace)
    assert TEST_PKG in str(first)


def test_reg_get(reg):
    name = reg.get(TEST_PKG)
    assert isinstance(name, Namespace)
    assert TEST_PKG in str(name)

    with raises(KeyError):
        reg.get("invalid")


def test_reg_name(reg):
    names = reg.get(TEST_PKG)
    assert isinstance(names, Namespace)
    assert "registry" in names.args
    assert reg.KEY_NS in names.args.keys()
    assert names.args[reg.KEY_NS] == TEST_PKG

    man = names.get(TEST_TAG)
    assert isinstance(man, Manifest)
    assert TEST_HASH in str(man)
    assert "registry" in man.args
    assert "namespace" in man.args
    assert reg.KEY_NS in man.args


def test_reg_name_latest(reg):
    name = reg.get(TEST_PKG)
    latest = name.get("latest")
    assert isinstance(latest, Manifest)
