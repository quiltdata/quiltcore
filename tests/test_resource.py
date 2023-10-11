from pytest import fixture

from quiltcore import Resource

from .conftest import TEST_VOL, not_win

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
    assert "Resource" in str(res)
    if not_win():
        assert TEST_VOL in repr(res)


def test_res_version():
    v = Resource.GetVersion(S3_URI)
    assert v == "123"
    path = Resource.AsPath(S3_URI)
    opts = {Resource.KEY_VER: v}
    res = Resource(path, **opts)
    assert res
    assert res.read_opts()[Resource.KEY_S3VER] == v

    assert res == Resource.FromURI(S3_URI)


def test_res_path():
    TEST_LOCAL = "./tests/example"
    path = Resource.AsPath(TEST_LOCAL)
    res = Resource(path)
    assert res
    assert res.path == path
    assert res.path.is_dir()
    assert res.path.exists()
