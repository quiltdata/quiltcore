from tempfile import TemporaryDirectory

from pytest import fixture, raises
from quiltcore import Manifest, Namespace, Volume

from .conftest import TEST_BKT, TEST_PKG, TEST_VOL
from upath import UPath


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def vol():
    return Volume.FromURI(TEST_VOL)


def test_vol(vol):
    assert vol
    assert vol.cf
    assert "volume" in vol.args


def test_vol_reg(vol):
    reg = vol.registry
    assert reg
    assert "volume" in reg.args


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


def test_vol_translate(dir: UPath):  # noqa: F401
    v_s3 = Volume.FromURI(TEST_BKT)
    assert v_s3
    pkg_s3 = v_s3.path / ".quilt/named_packages" / TEST_PKG
    assert pkg_s3.exists()
    man = v_s3.get(TEST_PKG)
    assert man

    v_tmp = Volume(dir)
    assert v_tmp
    pkg_tmp = v_tmp.path / ".quilt/named_packages" / TEST_PKG
    assert not pkg_tmp.exists()

    result = v_tmp.put(man, prefix = "data")
    assert result
    pkg_tmp = v_tmp.path / ".quilt/named_packages" / TEST_PKG
    # assert pkg_tmp.exists()
    

