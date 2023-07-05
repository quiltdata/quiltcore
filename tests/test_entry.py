from tempfile import TemporaryDirectory

from pytest import fixture
from quiltcore import Entry, Manifest
from upath import UPath

from .conftest import TEST_KEY, TEST_OBJ, TEST_OBJ_HASH, TEST_TABLE

DATA_HW = b"Hello world!"
HASH_HW = "c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a"
# w/o 1220 prefix


@fixture
def entry():
    path = UPath(TEST_TABLE)
    man = Manifest(path)
    entry: Entry = man.get(TEST_KEY)  # type: ignore
    return entry


def test_entry(entry: Entry):
    assert isinstance(entry.parent, Manifest)
    assert entry.logical_key == TEST_KEY  # type: ignore
    assert entry.physical_key == TEST_OBJ  # type: ignore
    assert entry.hash["value"] == TEST_OBJ_HASH  # type: ignore
    assert entry.hash["type"] == "SHA256"  # type: ignore
    assert entry.size == 100764599  # type: ignore

    assert entry.hash == TEST_OBJ_HASH
    assert entry.hash_type == "sha2-256"

    meta = entry.meta  # type: ignore
    assert meta
    assert isinstance(meta, dict)
    assert meta["target"] == "parquet"


def test_entry_put(entry: Entry):
    with TemporaryDirectory() as tmpdirname:
        dest = UPath(tmpdirname) / TEST_KEY
        loc = entry.put(dest)
        print(loc)
        assert TEST_KEY in str(loc)
        assert loc.exists()


def test_entry_digest(entry: Entry):
    assert entry.hash_digest
    digest = entry.hash_digest.digest(DATA_HW)
    assert digest.hex() == Entry.MH_PREFIX["SHA256"] + HASH_HW

    digest2 = entry.digest(DATA_HW)
    assert digest2 == HASH_HW


def test_entry_digest_verify(entry: Entry):
    entry.hash = HASH_HW
    assert entry.verify(DATA_HW)


def test_entry_verify(entry: Entry):
    assert entry.hash
    with TemporaryDirectory() as tmpdirname:
        dest = UPath(tmpdirname) / TEST_KEY
        entry.put(dest)
        assert dest.exists()
        bstring = dest.read_bytes()
        assert entry.verify(bstring)
