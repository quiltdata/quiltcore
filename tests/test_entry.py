from pathlib import Path

from pytest import fixture
from quiltcore import Entry, Manifest, Registry
from upath import UPath

from .conftest import TEST_KEY, TEST_MAN, TEST_OBJ_HASH

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
    entry: Entry = man.get(TEST_KEY)  # type: ignore
    return entry


def test_entry_init(entry: Entry):
    assert entry
    assert isinstance(entry, Entry)
    assert isinstance(entry.args["manifest"], Manifest)


def test_entry_setup(entry: Entry):
    assert entry.name == TEST_KEY
    # assert entry.path == TEST_OBJ
    assert entry.hash == TEST_OBJ_HASH
    assert entry.hash_type == "sha2-256"
    assert entry.size == 30


def test_entry_meta(entry: Entry):
    # TODO: choose a manifest with object-level metadata
    meta = entry.meta
    assert not meta
    # assert isinstance(meta, dict)
    # assert meta["target"] == "parquet"


def test_entry_get(entry: Entry, tmpdir: UPath):
    dest = tmpdir / "data"
    assert not dest.exists()

    loc = str(dest)
    clone = entry.get(loc)
    assert TEST_KEY in str(clone.path)
    assert entry.path != clone.path


def test_entry_digest(entry: Entry):
    digest2 = entry.digest(DATA_HW)
    assert digest2 == HASH_HW


def test_entry_hashable(entry: Entry):
    hashable = entry.to_hashable()
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
    assert entry.hash
    clone = entry.get(str(tmpdir))
    assert clone.path.exists()
    bstring = clone.to_bytes()
    assert entry.verify(bstring)


def test_entry_quote(entry: Entry):
    key = "s3://uri/with spaces"
    assert entry.encoded()
    encoded = entry.encode(key)
    assert encoded != key
    assert encoded == "s3://uri/with%20spaces"
