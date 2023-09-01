import pytest
from quiltcore import Codec, Domain, Factory, Keyed, Manifest2, Names, Node, Scheme, quilt
from upath import UPath

from .conftest import LOCAL_VOL, TEST_HASH, TEST_PKG, TEST_TAG

QKEYS = ["file", LOCAL_VOL, TEST_PKG, "latest"]
QTYPE = [Scheme, Domain, Names, Manifest2]
QMAP = dict(zip(QKEYS, QTYPE))
LOCAL_URI = "file://" + LOCAL_VOL


@pytest.fixture
def node():
    codec = Codec()
    return  Node(codec, "test", None)


def test_node(node):
    assert node is not None
    assert hasattr(node, "path")


def test_node_keyed():
    keyed = Keyed()
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
    assert isinstance(s3.parent, Factory)
    assert s3.name == "s3"
    assert quilt["file"] is not None


def test_node_uri():
    path = UPath(LOCAL_VOL)
    assert path.exists()

    udom = Domain.FromURI(LOCAL_URI)
    assert isinstance(udom, Domain)
    assert isinstance(udom.parent, Scheme)
    assert LOCAL_VOL == udom.name


def test_node_domain():
    f = quilt["file"]
    print(f"scheme[{f.name}]: {f}")
    dom = f[LOCAL_VOL]
    assert isinstance(dom, Domain)
    assert isinstance(dom.parent, Scheme)
    assert LOCAL_VOL in dom.keys()


def test_node_names():
    udom = Domain.FromURI(LOCAL_URI)
    ns = udom[TEST_PKG]
    assert TEST_PKG == ns.name
    assert isinstance(ns, Names)
    assert isinstance(ns.parent, Domain)

    q3hash = ns.get_q3hash(TEST_TAG)
    assert q3hash == TEST_HASH
    assert q3hash == ns.get_q3hash(TEST_HASH)
    assert q3hash == ns.get_q3hash(TEST_HASH[:6])

    with pytest.raises(ValueError):
        ns.get_q3hash("not-a-hash")
    with pytest.raises(ValueError):
        ns.get_q3hash("92") # ambiguous


def test_node_man():
    ns = Domain.FromURI(LOCAL_URI)[TEST_PKG]
    man = ns[TEST_TAG]
    assert isinstance(man, Manifest2)
    assert man.parent == ns
    assert man.q3hash() == TEST_HASH


@pytest.mark.skip(reason="TODO")
def test_node_tutorial():
    node = quilt
    for key in QMAP:
        node_type = QMAP[key]
        print(f"{key} -> {node_type.class_name} -> {node.name}")
        node = node[key]
        assert isinstance(node, QMAP[key])
