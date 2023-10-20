import pytest
from upath import UPath
from pathlib import Path
from tempfile import TemporaryDirectory


from quiltcore import (
    Codec,
    Domain,
    Table3,
    Entry2,
    Factory,
    Keyed,
    Manifest2,
    Namespace2,
    Node,
    Scheme,
    Types,
    quilt,
)

from .conftest import (
    LOCAL_ONLY,
    LOCAL_URI,
    LOCAL_VOL,
    TEST_HASH,
    TEST_MAN,
    TEST_PKG,
    TEST_S3VER,
    TEST_TAG,
)

QKEYS = ["file", LOCAL_VOL, TEST_PKG, "latest"]
QTYPE = [Scheme, Domain, Namespace2, Manifest2]
QMAP = dict(zip(QKEYS, QTYPE))


@pytest.fixture
def node():
    codec = Codec()
    return Node(codec, "test", None)


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
    assert LOCAL_VOL in udom.name


def test_node_names():
    udom = Domain.FromURI(LOCAL_URI)
    ns = udom[TEST_PKG]
    assert TEST_PKG == ns.name
    assert isinstance(ns, Namespace2)
    assert isinstance(ns.parent, Domain)

    q3hash = ns.read_hash_from_tag(TEST_TAG)
    assert q3hash == TEST_HASH
    assert q3hash == ns.read_hash_from_tag(TEST_HASH)
    assert q3hash == ns.read_hash_from_tag(TEST_HASH[:6])

    with pytest.raises(ValueError):
        ns.read_hash_from_tag("not-a-hash")
    with pytest.raises(ValueError):
        ns.read_hash_from_tag("92")  # ambiguous


def test_node_man():
    ns = Domain.FromURI(LOCAL_URI)[TEST_PKG]
    man = ns[TEST_TAG]
    assert isinstance(man, Manifest2)
    assert man.q3hash() == TEST_HASH
    assert man.parent == ns

    path = man.extend_parent_path(TEST_HASH)
    assert path == man.path
    assert str(ns.manifests) in str(path)

    assert man.path.exists()


def test_node_entry():
    man = Domain.FromURI(LOCAL_URI)[TEST_PKG][TEST_TAG]
    store = Domain.FindStore(man)
    assert store
    for key in man:
        entry = man[key]
        assert entry is not None
        assert entry.name == key
        assert isinstance(entry, Entry2)
        assert entry.path.exists()
        assert entry.path.is_relative_to(store)


def test_node_children():
    node = quilt
    for key in QMAP:
        node_type = QMAP[key]
        node = node[key]
        assert isinstance(node, node_type)
    assert node.path.exists()


@pytest.mark.skipif(LOCAL_ONLY, reason="skip network tests")
def test_node_path():
    p1 = Types.AsPath(TEST_S3VER)
    assert p1.exists()
    p2 = Types.AsPath(LOCAL_URI)
    assert p2.is_absolute()
    assert p2.exists()
    p3 = Types.AsPath("file://./path")
    assert not p3.exists()


def test_node_save_manifest():
    path = Types.AsPath(TEST_MAN)
    table3 = Table3(path)
    man = Domain.FromURI(LOCAL_URI)[TEST_PKG][TEST_TAG]

    with TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        list4 = table3.relax(root)
        pout = root / "test.parquet"
        man.save_manifest(list4, pout, True)
