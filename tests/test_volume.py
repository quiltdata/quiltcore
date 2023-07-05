from pytest import fixture, raises
from quiltcore import Manifest, Namespace, Volume

from .conftest import dir, TEST_BKT, TEST_PKG, UPath  # noqa: F401


@fixture
def vol():
    path_bkt = UPath(TEST_BKT)
    return Volume(path_bkt)


def test_vol(vol):
    assert vol
    assert vol.cf
    assert "Volume" in vol.args


def test_vol_reg(vol):
    reg = vol.registry
    assert reg
    assert "Volume" in reg.args


def test_vol_get(vol):
    man = vol.get(TEST_PKG)
    assert isinstance(man, Manifest)

    with raises(KeyError):
        vol.get("invalid")


def test_vol_list(vol):
    result = vol.list()
    assert isinstance(result, list)
    assert len(result) == 0
    
    vol.get(TEST_PKG)
    results = vol.list()
    assert len(results) == 1
    assert isinstance(results[0], Manifest)


def test_vol_man_latest(vol):
    man = vol.get(TEST_PKG, tag="latest")
    assert isinstance(man, Manifest)

def test_vol_translate(vol):
    assert vol

