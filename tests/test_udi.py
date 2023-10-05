import pytest
from quiltcore import UDI

from .conftest import (
    BKT_URI,
    PTH_URI,
    T_BKT,
    T_PKG,
    TEST_URI,
)


@pytest.fixture
def uri():
    return UDI.FromUri(TEST_URI)


def test_uri(uri: UDI):
    assert uri.uri == TEST_URI
    assert uri.registry == f"s3://{T_BKT}"
    assert uri.package == T_PKG


def test_uri_repr(uri: UDI):
    assert TEST_URI in repr(uri)
    assert uri == uri


def test_uri_eq(uri: UDI):
    assert uri == uri
    uri_pth = UDI.FromUri(PTH_URI)
    assert uri_pth == uri
    uri_bkt = UDI.FromUri(BKT_URI)
    assert uri_bkt != uri


def test_uri_null():
    un = UDI({})
    assert un
    assert un.uri is None
