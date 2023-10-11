from tempfile import TemporaryDirectory

import pytest

from quiltcore import UDI, Domain, Scheme, quilt

from .conftest import LOCAL_UDI, LOCAL_URI, LOCAL_VOL, TEST_HASH, TEST_PKG, not_win


@pytest.fixture
def domain():
    with TemporaryDirectory() as tmpdirname:
        f = quilt["file"]
        dom = f[tmpdirname]
        dom.is_mutable = True
        yield dom


@pytest.fixture
def remote_udi():
    return UDI.FromUri(LOCAL_UDI)


def test_pull_udi_scheme():
    assert "quilt+file://" in LOCAL_UDI
    f = quilt["file"]
    dom = f[LOCAL_VOL]
    assert isinstance(dom, Domain)
    assert isinstance(dom.parent, Scheme)
    assert LOCAL_VOL == dom.cf.AsStr(dom.store)


def test_pull_udi(domain: Domain, remote_udi: UDI):
    assert remote_udi
    assert remote_udi.uri == LOCAL_UDI
    assert remote_udi.package == TEST_PKG
    print(f"LOCAL_URI: {LOCAL_URI}")
    posix_path = domain.cf.AsPath(LOCAL_URI)
    print(f"posix_path: {posix_path}")
    posix_vol = domain.cf.AsStr(posix_path)
    print(f"posix_vol: {posix_vol}")
    assert remote_udi.registry == LOCAL_URI


def test_pull_raise(domain: Domain, remote_udi: UDI):
    domain.is_mutable = False
    with pytest.raises(AssertionError):
        domain.pull(remote_udi, dest=None)


@pytest.mark.skipif(not_win(), reason="Does not work on Windows")
def test_pull_data_yaml(domain: Domain, remote_udi: UDI):
    dy = domain.data_yaml
    assert dy
    assert dy.path
    assert not dy.path.exists()
    path = domain.pull(remote_udi, hash=TEST_HASH)
    assert dy.path.exists()

    dest = str(path)
    assert TEST_PKG in dest
    assert dy.get_uri(dest) == LOCAL_UDI
    assert dy.get_folder(LOCAL_UDI) == dest

    status = dy.get_list(dest, LOCAL_UDI, "pull")
    assert isinstance(status, dict)
    assert "timestamp" in status
    assert "user" in status
    assert status["hash"] == TEST_HASH
