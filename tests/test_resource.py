from pytest import fixture, raises
from quiltcore import Resource
from upath import UPath

from .conftest import TEST_HASH, TEST_PKG, TEST_TAG, TEST_VOL

@fixture
def reg():
    path_bkt = UPath(TEST_VOL)
    return Resource(path_bkt)

def test_reg(reg):
    assert reg
    assert reg.cf
    assert reg.path.is_dir()
    assert "resource" in reg.args

def test_reg_version():
    uri_string = "s3://bkt?versionId=123"
    v = Resource.GetVersion(uri_string)
    assert v == "123"
    path = Resource.AsPath(uri_string)
    opts = {Resource.KEY_VER: v}
    res = Resource(path, **opts)
    assert res
    assert res.read_opts()[Resource.KEY_S3VER] == v