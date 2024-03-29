from tempfile import TemporaryDirectory

import pytest
from upath import UPath

from quiltcore import Codec, Domain, Entry, Header, Manifest, Table4, quilt

from .conftest import (
    LOCAL_ONLY,
    LOCAL_URI,
    TEST_HASH,
    TEST_KEY,
    TEST_OBJ,
    TEST_OBJ_HASH,
    TEST_PKG,
    TEST_S3VER,
    TEST_VER,
)


def dump_manifest(domain: Domain, pkg_name: str):
    manifest = domain[pkg_name]["latest"]
    print(f"manifest: {manifest}")
    print(f"manifest: {manifest.path}")
    table4 = Table4(manifest.path)
    print(f"table4:\n{table4}")
    assert False


@pytest.fixture
def man() -> Manifest:
    ns = Domain.FromURI(LOCAL_URI)[TEST_PKG]
    return ns[TEST_HASH]


@pytest.fixture
def domain():
    with TemporaryDirectory() as tmpdirname:
        f = quilt["file"]
        dom = f[tmpdirname]
        yield dom


def test_man(man: Manifest):
    assert man
    assert "manifest" in man.args.keys()
    assert man._table is not None
    assert man.table() is not None
    assert man.path.exists()


def test_man_head(man: Manifest):
    head = man.header()
    assert isinstance(head, Header)

    hashable = head.hashable_dict()
    assert hashable
    assert isinstance(hashable, dict)
    assert hashable["user_meta"]["Author"] == "Ernest"


@pytest.mark.skipif(LOCAL_ONLY, reason="skip network tests")
def test_man_version(man: Manifest):
    path = UPath(TEST_S3VER)
    version = Codec.StatVersion(path)
    assert version

    bad_path = UPath(TEST_OBJ)
    bad_version = Codec.StatVersion(bad_path)
    assert not bad_version
    remote = quilt["s3"]["quilt-example"]["akarve/amazon-reviews"]["1570503102"][
        "camera-reviews"
    ]
    assert isinstance(remote, Entry)


def test_man_entry(man: Manifest):
    entry = man[TEST_KEY]
    # assert entry
    assert isinstance(entry, Entry)
    assert entry.args

    version = entry.GetQuery(TEST_S3VER, entry.K_VER)
    assert version == TEST_VER


def test_man_list(man: Manifest):
    results = man.values()
    assert len(results) == 2
    entry = list(results)[1]
    assert isinstance(entry, Entry)
    assert TEST_KEY in str(entry.path)


def test_man_install(man: Manifest, domain: Domain):
    entry = man[TEST_KEY]
    assert "manifest" in entry.args
    assert isinstance(entry, Entry)
    assert TEST_KEY in str(entry.path)

    dest = domain.store
    assert dest.exists()
    clone = entry.install(str(dest))
    assert TEST_KEY in str(clone.path)
    # assert entry.path != clone.path


def test_man_hash(man: Manifest):
    hash = man.q3hash()
    assert hash == man.name


@pytest.mark.skip("Confused OBJ vs ENTRY hash")
def test_man_entry_hash(man: Manifest):
    entry = man[TEST_KEY]
    hashable = entry.hashable_dict()
    assert hashable
    assert isinstance(hashable, dict)
    assert hashable["logical_key"] == TEST_KEY
    assert hashable["size"] == 30
    assert hashable["hash"]["value"] == TEST_OBJ_HASH
    assert hashable["meta"] == {}
    assert entry.multihash == entry.hash()


def test_man_relax(man: Manifest, domain: Domain):
    ns = domain[TEST_PKG]
    local_man = man.relax(domain.store, ns.relax_params())
    assert local_man is not None
    assert isinstance(local_man, Manifest)
    assert local_man.path.exists()
    assert domain.store in local_man.path.parents
    assert local_man.hashify() == man.hashify()  # TODO: force recalculation
