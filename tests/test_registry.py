from pytest import fixture, raises
from quiltcore import Manifest, Namespace, Registry

from .conftest import TEST_PKG, TEST_VOL


@fixture
def reg():
    path_bkt = Manifest.AsPath(TEST_VOL)
    return Registry(path_bkt)


def test_reg(reg):
    assert reg
    assert reg.cf
    assert ".quilt/named_packages" in str(reg.path.as_posix())
    assert ".quilt/packages" in str(reg.manifests.as_posix())
    assert reg.manifests.exists()
    assert reg.path.is_dir()
    assert "registry" in reg.args


def test_reg_map(reg):
    assert reg
    assert reg.__len__() > 0
    name = reg[TEST_PKG]
    assert isinstance(name, Namespace)
    assert name in reg.values()
    assert TEST_PKG in reg.keys()


def test_reg_eq(reg):
    path = Manifest.AsPath(TEST_VOL)
    reg2 = Registry(path)
    assert reg == reg2
    assert reg == reg.args["registry"]


def test_reg_list(reg):
    result = reg.list()
    assert isinstance(result, list)
    assert len(result) > 0
    first = result[0]
    assert isinstance(first, Namespace)
    assert TEST_PKG in str(first.path.as_posix())


def test_reg_get(reg):
    name = reg.getResource(TEST_PKG)
    assert isinstance(name, Namespace)
    assert TEST_PKG in str(name.path.as_posix())

    with raises(KeyError):
        reg.getResource("invalid")


def test_reg_new(reg):
    NEW_PKG = f"test/test_reg_new_{Registry.Now()}"
    with raises(KeyError):
        reg.getResource(NEW_PKG)
    force = {Registry.KEY_FRC: True}
    new_pkg = reg.getResource(NEW_PKG, **force)
    assert new_pkg != None
    assert isinstance(new_pkg, Namespace)
