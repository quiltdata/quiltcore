from tempfile import TemporaryDirectory
from pytest import fixture, mark

from quiltcore import (
    Domain,
    Scheme,
    quilt,
    UDI
)

from .conftest import LOCAL_UDI, LOCAL_VOL, TEST_HASH, TEST_PKG, TEST_TAG


@fixture
def domain():
    with TemporaryDirectory() as tmpdirname:
        f = quilt["file"]
        dom = f[tmpdirname]
        return dom

@fixture
def udi():
    return UDI.FromUri(LOCAL_UDI)

def test_pull_domain():
    f = quilt["file"]
    print(f"scheme[{f.name}]: {f}")
    dom = f[LOCAL_VOL]
    assert isinstance(dom, Domain)
    assert isinstance(dom.parent, Scheme)
    assert LOCAL_VOL in dom.keys()
    assert "quilt+file://" in LOCAL_UDI


def test_pull_udi(udi: UDI):
    assert udi
    assert udi.uri == LOCAL_UDI
    assert udi.package == TEST_PKG
    assert udi.registry.startswith("file://" + LOCAL_VOL)


def test_pull(domain: Domain, udi: UDI):
    assert domain is not None
    assert isinstance(domain, Domain)
    result = domain.pull(udi)
    assert result

