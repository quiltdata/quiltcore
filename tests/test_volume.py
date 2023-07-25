from tempfile import TemporaryDirectory

from pytest import fixture, mark, raises
from quiltcore import Manifest, Volume
from upath import UPath

from .conftest import LOCAL_ONLY, TEST_BKT, TEST_HASH, TEST_PKG, TEST_VOL


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
    assert vol.is_local()


def test_vol_reg(vol):
    reg = vol.registry
    assert reg
    assert "volume" in reg.args


def test_vol_get(vol):
    man = vol.get(TEST_PKG)
    assert isinstance(man, Manifest)
    vol.delete(TEST_PKG)

    opts = {vol.KEY_HSH: TEST_HASH}
    man2 = vol.get(TEST_PKG, **opts)
    assert isinstance(man2, Manifest)
    vol.delete(TEST_PKG)

    with raises(KeyError):
        vol.get("invalid")

    with raises(KeyError):
        vol.delete(TEST_PKG)


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


@mark.skipif(LOCAL_ONLY, reason="skip network tests")
def test_vol_put(dir: UPath):  # noqa: F401
    v_s3 = Volume.FromURI(TEST_BKT)
    assert not v_s3.is_local()
    pkg_s3 = v_s3.registry.path / TEST_PKG
    assert pkg_s3.exists()
    man = v_s3.get(TEST_PKG)
    assert man

    v_tmp = Volume(dir)
    pkg_tmp = v_tmp.registry.path / TEST_PKG
    assert not pkg_tmp.exists()

    man2: Manifest = v_tmp.put(man)  # type: ignore
    assert pkg_tmp.exists()
    assert man2.path.exists()

    hash = man2.hash_quilt3()
    assert hash == man2.name

    latest = pkg_tmp / Volume.TAG_DEFAULT
    assert latest.exists()
    hash = latest.read_text()
    assert hash == man2.name
