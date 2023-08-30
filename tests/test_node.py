import pytest
from quiltcore import Codec, Domain, Factory, Keyed, Manifest, Namespace, Node, Scheme, quilt

from .conftest import LOCAL_VOL, TEST_PKG

QKEYS = ["file", LOCAL_VOL, TEST_PKG, "latest"]
QTYPE = [Scheme, Domain, Namespace, Manifest]
QMAP = dict(zip(QKEYS, QTYPE))


@pytest.fixture
def node():
    codec = Codec()
    return  Node(codec, "test", None)


def test_node(node):
    assert node is not None


def test_node_keyed():
    keyed = Keyed()
    assert keyed.cache is not None
    assert len(keyed) == 0

    keyed["key"] = "value"
    assert keyed.get("key") == "value"
    assert keyed["key"] == "value"
    assert len(keyed) == 1

    del keyed["key"]
    assert len(keyed) == 0


def test_node_factory():
    assert isinstance(quilt, Factory)
    assert quilt.name == "quilt"


def test_node_scheme():
    s3 = quilt["s3"]
    assert isinstance(s3, Scheme)
    assert s3.name == "s3"
    assert quilt["file"] is not None


def test_node_domain():
    f = quilt["file"]
    dom = f[LOCAL_VOL]
    assert isinstance(dom, Domain)

    uri = "file://" + LOCAL_VOL
    Domain.FromURI(uri)


@pytest.mark.skip(reason="TODO")
def test_node_tutorial():
    node = quilt
    for key in QMAP:
        node_type = QMAP[key]
        print(f"{key} -> {node_type.class_name} -> {node.name}")
        node = node[key]
        assert isinstance(node, QMAP[key])
