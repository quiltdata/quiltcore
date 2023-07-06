from pytest import fixture, raises
from quiltcore import Manifest, Namespace, Registry
from upath import UPath

from .conftest import TEST_VOL, TEST_HASH, TEST_PKG, TEST_TAG


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
    print(result)
    first = result[0]
    print(first)
    assert isinstance(first, Namespace)
    assert TEST_PKG in str(first)


def test_reg_get(reg):
    name = reg.get(TEST_PKG)
    assert isinstance(name, Namespace)
    assert TEST_PKG in str(name)

    with raises(KeyError):
        reg.get("invalid")


def test_reg_name(reg):
    name = reg.get(TEST_PKG)
    assert isinstance(name, Namespace)
    assert "registry" in name.args
    ns_key = "namespace._key"
    assert ns_key in name.args.keys()
    assert name.args[ns_key] == TEST_PKG

    man = name.get(TEST_TAG)
    assert isinstance(man, Manifest)
    assert TEST_HASH in str(man)
    assert "registry" in man.args
    assert "namespace" in man.args
    assert ns_key in man.args

def test_reg_name_latest(reg):
    name = reg.get(TEST_PKG)
    latest = name.get("latest")
    assert isinstance(latest, Manifest)

