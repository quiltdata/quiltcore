from pytest import fixture, mark

from quiltcore import (
    Builder2,
    Domain,
    Manifest2,
)

from .conftest import LOCAL_URI, LOCAL_VOL, TEST_HASH, TEST_PKG, TEST_TAG

# skip all tests in this module
pending = mark.skip("change module not implemented")

@fixture
def man() -> Manifest2:
    ns = Domain.FromURI(LOCAL_URI)[TEST_PKG]
    return ns[TEST_HASH]

def test_dom_pull():
    pass
