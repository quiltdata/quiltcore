from tempfile import TemporaryDirectory

import pytest

from quiltcore import UDI, Domain, Scheme, quilt

from .conftest import LOCAL_UDI, LOCAL_VOL, TEST_HASH, TEST_PKG, TEST_VOL


@pytest.fixture
def domain():
    with TemporaryDirectory() as tmpdirname:
        f = quilt["file"]
        dom = f[tmpdirname]
        dom.is_mutable = True
        yield dom


@pytest.fixture
def udi():
    return UDI.FromUri(LOCAL_UDI)


def test_pull_domain():
    assert "quilt+file://" in LOCAL_UDI
    f = quilt["file"]
    dom = f[LOCAL_VOL]
    assert isinstance(dom, Domain)
    assert isinstance(dom.parent, Scheme)
    assert LOCAL_VOL == str(dom.store)


def test_pull_udi(udi: UDI):
    assert udi
    assert udi.uri == LOCAL_UDI
    assert udi.package == TEST_PKG
    assert udi.registry == "file://" + TEST_VOL


def test_pull_call(domain: Domain, udi: UDI):
    assert domain is not None
    assert isinstance(domain, Domain)
    result = domain.pull(udi)
    assert result


def test_pull_raise(domain: Domain, udi: UDI):
    domain.is_mutable = False
    with pytest.raises(AssertionError):
        domain.pull(udi, dest=None)


def test_pull_data_yaml(domain: Domain, udi: UDI):
    assert domain.data_yaml
    assert domain.data_yaml.path
    assert not domain.data_yaml.path.exists()
    path = domain.pull(udi, hash=TEST_HASH)
    dest = str(path)
    assert domain.data_yaml.path.exists()
    assert dest == TEST_PKG
    assert domain.data_yaml.get_uri(dest) == LOCAL_UDI
    assert domain.data_yaml.get_folder(LOCAL_UDI) == dest
    print(f"domain.data_yaml: {domain.data_yaml.data}")
    status = domain.data_yaml.get_list(dest, LOCAL_UDI, "pull")
    print(f"status: {status}")
    assert isinstance(status, dict)
    assert "timestamp" in status
    assert "user" in status
    assert status["hash"] == TEST_HASH
