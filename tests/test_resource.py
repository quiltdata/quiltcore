from pathlib import Path

from pytest import fixture, mark
from quiltcore import Resource

from .conftest import LOCAL_VOL, TEST_PKG, TEST_VOL

S3_URI = "s3://bkt?versionId=123"


@fixture
def res():
    path_bkt = Resource.AsPath(TEST_VOL)
    return Resource(path_bkt)


def test_res(res):
    assert res
    assert res.cf
    assert res.path.is_dir()
    assert "resource" in res.args


def test_res_version():
    v = Resource.GetVersion(S3_URI)
    assert v == "123"
    path = Resource.AsPath(S3_URI)
    opts = {Resource.KEY_VER: v}
    res = Resource(path, **opts)
    assert res
    assert res.read_opts()[Resource.KEY_S3VER] == v

    assert res == Resource.FromURI(S3_URI)


@mark.skip(reason="Not implemented")
def test_res_path():
    assert Resource.PathIfLocal(S3_URI) is None
    key = TEST_PKG
    root = Path.cwd() / LOCAL_VOL
    abs_path = root / TEST_PKG
    assert Resource.PathIfLocal(key) == abs_path
