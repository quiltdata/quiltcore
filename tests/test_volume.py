from tempfile import TemporaryDirectory

from pytest import fixture, mark, raises
from quiltcore import Manifest, Volume
from upath import UPath

from .conftest import LOCAL_ONLY, TEST_BKT, TEST_HASH, TEST_PKG, TEST_VOL, MockChanges


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
    man = vol.getResource(TEST_PKG)
    assert isinstance(man, Manifest)
    vol.delete(TEST_PKG)

    hash = man.name
    man_hash = vol.getResource("", **{man.KEY_HSH: hash})
    assert man_hash.name == hash
    assert man_hash == man

    man2 = vol.getResource(TEST_PKG, **{vol.KEY_HSH: TEST_HASH})
    assert isinstance(man2, Manifest)
    vol.delete(TEST_PKG)

    with raises(KeyError):
        vol.getResource("invalid")

    with raises(KeyError):
        vol.delete(TEST_PKG)


def test_vol_stage(vol):
    """If a given hash is locally staged, use that instead"""
    pass


def test_vol_man(vol):
    man = vol.getResource(TEST_PKG)
    name = vol.registry.getResource(TEST_PKG)
    tag = vol.TAG_DEFAULT
    hash = name.hash(tag)
    assert hash == man.name


def test_vol_list(vol):
    result = vol.list()
    assert isinstance(result, list)
    assert len(result) == 0

    vol.getResource(TEST_PKG)
    results = vol.list()
    assert len(results) == 1
    assert isinstance(results[0], Manifest)


def test_vol_man_latest(vol):
    man = vol.getResource(TEST_PKG, tag="latest")
    assert isinstance(man, Manifest)


@mark.skipif(LOCAL_ONLY, reason="skip network tests")
def test_vol_put(dir: UPath):  # noqa: F401
    v_s3 = Volume.FromURI(TEST_BKT)
    assert not v_s3.is_local()
    pkg_s3 = v_s3.registry.path / TEST_PKG
    assert pkg_s3.exists()
    man = v_s3.getResource(TEST_PKG)
    assert man

    v_tmp = Volume(dir)
    pkg_tmp = v_tmp.registry.path / TEST_PKG
    assert not pkg_tmp.exists()

    man2: Manifest = v_tmp.put(man, **{man.KEY_NS: TEST_PKG})  # type: ignore
    assert man2.path.exists()
    assert man2.name == man2.hash_quilt3()
    assert man.KEY_TAG in man2.args

    assert pkg_tmp.exists()
    latest = pkg_tmp / Volume.TAG_DEFAULT
    assert latest.exists()
    assert man2.name == latest.read_text()

@mark.skip("Not fully implemented")
def test_vol_post(dir: UPath):  # noqa: F401
    """Use Volume to create a new manifest from a folder in a Volume"""
    vol = Volume(dir)
    subdir = vol.path / "sub"
    chg = MockChanges(subdir)

    assert chg.path.exists()
    man = vol.post(subdir, **chg.args)
    assert man
    assert man.path.exists()
    assert isinstance(man, Manifest)
    assert vol.registry.manifests / man.name == man.path


