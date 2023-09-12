from quiltcore import (
    Domain,
    Scheme,
    quilt,
)

from .conftest import LOCAL_URI, LOCAL_VOL, TEST_HASH, TEST_PKG, TEST_TAG

def test_dom():
    f = quilt["file"]
    print(f"scheme[{f.name}]: {f}")
    dom = f[LOCAL_VOL]
    assert isinstance(dom, Domain)
    assert isinstance(dom.parent, Scheme)
    assert LOCAL_VOL in dom.keys()

def test_dom_pull():
    pass
