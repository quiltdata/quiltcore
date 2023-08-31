from pathlib import Path

from pytest import fixture, mark
from quiltcore import Entry, Manifest, Registry
from upath import UPath

from .conftest import LOCAL_ONLY, TEST_BKT, TEST_KEY, TEST_MAN, TEST_OBJ_HASH

DATA_HW = b"Hello world!"
HASH_HW = "1220c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a"
# with Multhash prefix 1220


@fixture
def man() -> Manifest:
    root = Path.cwd() / "tests" / "example"
    opts = {"registry": Registry(root)}
    path = Manifest.AsPath(TEST_MAN)
    man = Manifest(path, **opts)
    return man


@fixture
def entry(man: Manifest) -> Entry:
    entry: Entry = man.getResource(TEST_KEY)  # type: ignore
    return entry


def test_entry_init(entry: Entry):
    # assert entry
    assert isinstance(entry, Entry)
    assert isinstance(entry.args["manifest"], Manifest)


def test_entry_setup(entry: Entry):
    assert entry.name == TEST_KEY
    assert entry.hash_quilt3() == TEST_OBJ_HASH
    assert entry.size == 30


def test_entry_meta(entry: Entry):
    # TODO: choose a manifest with object-level metadata
    meta = entry.meta
    assert not meta


def test_entry_get(entry: Entry, tmpdir: UPath):
    dest = tmpdir / "data"
    assert not dest.exists()
    clone = entry.install(str(dest))
    assert TEST_KEY in str(clone.path)
    assert entry.path != clone.path


@mark.skipif(LOCAL_ONLY, reason="skip network tests")
def test_entry_remote(entry: Entry):
    remote = UPath(TEST_BKT) / "spec"
    clone = entry.install(str(remote))
    assert clone.path.exists()
    place = clone.args[clone.cf.K_PLC]
    query = place.split("?")
    assert query
    assert len(query) > 1, "has query string"
    assert clone.KEY_VER in query[1]


def test_entry_digest(entry: Entry):
    digest2 = entry.digest_bytes(DATA_HW)
    assert digest2 == HASH_HW


def test_entry_hashable(entry: Entry):
    hashable = entry.hashable_dict()
    assert hashable
    assert isinstance(hashable, dict)
    assert hashable["logical_key"] == TEST_KEY
    assert hashable["size"] == 30
    assert hashable["hash"]["value"] == TEST_OBJ_HASH
    assert hashable["meta"] == {}


def test_entry_digest_verify(entry: Entry):
    entry.multihash = HASH_HW
    assert entry.verify(DATA_HW)


def test_entry_verify(entry: Entry, tmpdir: UPath):
    assert entry.multihash
    clone = entry.install(str(tmpdir))
    assert clone.path.exists()
    bstring = clone.to_bytes()
    assert entry.verify(bstring)
