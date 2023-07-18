from tempfile import TemporaryDirectory

from pytest import fixture, raises
from quiltcore import Manifest, Volume
from upath import UPath

from .conftest import TEST_BKT, TEST_PKG, TEST_VOL


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


def test_vol_put(dir: UPath):  # noqa: F401
    v_s3 = Volume.FromURI(TEST_BKT)
    pkg_s3 = v_s3.registry.path / TEST_PKG
    assert pkg_s3.exists()
    man = v_s3.get(TEST_PKG)
    assert man

    v_tmp = Volume(dir)
    pkg_tmp = v_tmp.registry.path / TEST_PKG
    assert not pkg_tmp.exists()

    man2 = v_tmp.put(man)
    assert pkg_tmp.exists()
    assert man2.path.exists()

    hash = man2.calc_multihash()  # type: ignore
    # assert hash == man2.name

    latest = pkg_tmp / Volume.TAG_DEFAULT
    assert latest.exists()
    hash = latest.read_text()
    assert hash == man2.name
