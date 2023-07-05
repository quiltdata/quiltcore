from tempfile import TemporaryDirectory

from pytest import fixture, mark
from quiltcore import Entry, Manifest
from upath import UPath

from .conftest import TEST_KEY, TEST_OBJ_HASH, TEST_TABLE

DATA_HW = b"Hello world!"
HASH_HW = "1220c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a"
# with Multhash prefix 1220


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def man() -> Manifest:
    man = Manifest(UPath(TEST_TABLE))
    return man


@fixture
def entry(man: Manifest) -> Entry:
    man = Manifest(UPath(TEST_TABLE))
    entry: Entry = man.get(TEST_KEY)  # type: ignore
    return entry


def test_entry_init(entry: Entry):
    assert entry
    assert isinstance(entry, Entry)
    print(entry.args.keys())
    assert isinstance(entry.args["manifest"], Manifest)


def test_entry_setup(entry: Entry):
    assert entry.name == TEST_KEY
    # assert entry.path == TEST_OBJ
    assert entry.hash == TEST_OBJ_HASH
    assert entry.hash_type == "sha2-256"
    assert entry.size == 30


@mark.skip
def test_entry_meta(entry: Entry):
    meta = entry.meta
    assert meta
    assert isinstance(meta, dict)
    assert meta["target"] == "parquet"


def test_entry_get(entry: Entry, dir: UPath):
    dest = dir / TEST_KEY
    assert not dest.exists()

    loc = str(dest)
    entry.get(loc)
    assert TEST_KEY in loc


def test_entry_digest(entry: Entry):
    digest2 = entry.digest(DATA_HW)
    assert digest2 == HASH_HW


def test_entry_digest_verify(entry: Entry):
    entry.multihash = HASH_HW
    assert entry.verify(DATA_HW)


def test_entry_verify(entry: Entry, dir: UPath):
    assert entry.hash
    dest = dir / TEST_KEY
    loc = str(dest)
    entry.get(loc)
    assert dest.exists()
    bstring = dest.read_bytes()
    assert entry.verify(bstring)
