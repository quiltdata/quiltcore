from tempfile import TemporaryDirectory

import pytest

from quiltcore import UDI, Domain, Scheme, quilt

from .conftest import LOCAL_UDI, LOCAL_URI, LOCAL_VOL, TEST_HASH, TEST_PKG, not_win


def make_domain():
    with TemporaryDirectory() as tmpdirname:
        f = quilt["file"]
        dom = f[tmpdirname]
        dom.is_mutable = True
        yield dom


@pytest.fixture
def domain():
    for dom in make_domain():
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
    assert LOCAL_VOL in dom.cf.AsStr(dom.store)


def test_pull_remote_udi(remote_udi: UDI):
    assert remote_udi
    assert remote_udi.uri == LOCAL_UDI
    assert remote_udi.package == TEST_PKG
    if not_win():
        assert remote_udi.registry == LOCAL_URI


def test_pull_uri(domain: Domain):
    uri = domain.get_uri()
    assert uri.startswith("file:///")
    domain2 = Domain.FromURI(uri)
    assert domain2.store == domain.store


def test_pull_udi(domain: Domain):
    udi = domain.get_udi_string()
    assert udi.startswith("quilt+file:///")
    udip = domain.get_udi_string(TEST_PKG)
    assert udip.endswith(f"#package={TEST_PKG}")
    udipp = domain.get_udi_string(TEST_PKG, "README.md")
    assert udipp.endswith(f"#package={TEST_PKG}&path=README.md")


def test_pull_raise(domain: Domain, remote_udi: UDI):
    domain.is_mutable = False
    with pytest.raises(AssertionError):
        domain.pull(remote_udi, dest=None)


def test_pull_data_yaml(domain: Domain, remote_udi: UDI):
    dy = domain.data_yaml
    assert dy
    assert dy.path
    assert not dy.path.exists()
    path = domain.pull(remote_udi, hash=TEST_HASH)
    assert dy.path.exists()

    dest = str(path)
    assert TEST_PKG in dest
    assert dy.folder2uri(dest) == LOCAL_UDI
    assert dy.uri2folder(LOCAL_UDI) == dest

    status = dy.get_list(dest, LOCAL_UDI, "pull")
    assert isinstance(status, dict)
    assert "timestamp" in status
    assert "user" in status
    assert status["hash"] == TEST_HASH


def test_pull_push():
    for local in make_domain():
        local_path = local.package_path(TEST_PKG)
        assert local_path.exists()
        readme = local_path / "README.md"
        readme.write_text("Hello World")
        local.commit(local_path, package=TEST_PKG, msg=f"test_pull_push {Domain.Now()}")
        # local.push(local_path)
    for remote in make_domain():
        assert isinstance(remote, Domain)
        remote_udi = remote.get_udi(TEST_PKG)
        assert remote_udi
