import pytest

from quiltcore import Codec, Domain, Factory, Manifest, Namespace, Node, Scheme, quilt

from .conftest import LOCAL_VOL, TEST_PKG

QKEYS = ["file", LOCAL_VOL, TEST_PKG, "latest"]
QTYPE = [Scheme, Domain, Namespace, Manifest]
QMAP = dict(zip(QKEYS, QTYPE))

def test_node():
    codec = Codec()
    node = Node(codec, "test", None)
    assert node

def test_node_factory():
    assert quilt
    assert isinstance(quilt, Factory)
    assert quilt.name == "quilt"

def test_node_scheme():
    s3 = quilt["s3"]
    assert s3
    assert isinstance(s3, Scheme)
    assert s3.name == "s3"
    assert quilt["file"]

def test_node_domain():
    f = quilt["file"]
    dom = f[LOCAL_VOL]
    assert dom
    assert isinstance(dom, Domain)

    uri = "file://" + LOCAL_VOL
    dom2 = Domain.FromURI(uri)

@pytest.mark.skip(reason="TODO")
def test_node_tutorial():
    node = quilt
    for key in QMAP:
        node_type = QMAP[key]
        print(f"{key} -> {node_type.class_name} -> {node.name}")
        node = node[key]
        assert isinstance(node, QMAP[key])
