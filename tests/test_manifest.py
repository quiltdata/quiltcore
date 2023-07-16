from tempfile import TemporaryDirectory

from pathlib import Path
from pytest import fixture
from quiltcore import Entry, Manifest, Registry
from upath import UPath

from .conftest import TEST_KEY, TEST_OBJ_HASH, TEST_S3VER, TEST_SIZE, TEST_MAN

K_REG = "registry"


@fixture
def tmpdir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def man():
    opts = {}
    path = Manifest.AsPath(TEST_MAN)
    return Manifest(path, **opts)


def test_man(man: Manifest):
    assert man
    assert "manifest" in man.args


def test_man_head(man: Manifest):
    head = man.head
    assert head
    assert head.version == "v0"  # type: ignore
    assert len(head.message) > 0  # type: ignore
    assert len(head.user_meta) > 0  # type: ignore
    assert head.user_meta["Author"] == "Ernest"  # type: ignore

    hashable = head.to_hashable()
    assert hashable
    assert isinstance(hashable, dict)
    assert hashable["Author"] == "Ernest"


def test_man_table(man: Manifest):
    assert man.table
    assert man.body
    assert man.body.num_rows == 1
    schema = man.body.schema
    assert schema
    columns = man.cf.get_dict("quilt3/columns")
    for key in columns:
        assert key in schema.names


def test_man_child_place():
    rootdir = Path.cwd()
    root = str(rootdir)
    opts = {K_REG: Registry(rootdir)}
    path = Manifest.AsPath(TEST_MAN)
    man = Manifest(path, **opts)
    assert K_REG in man.args

    assert TEST_S3VER == man._child_place(TEST_S3VER)
    assert TEST_S3VER == man._child_place([TEST_S3VER])
    TEST_LOCAL = man.LOCAL+"place"
    TEST_GLOBAL = str(rootdir / "place")
    print(man.args.keys())
    assert man._child_place(TEST_LOCAL, root) == TEST_GLOBAL

def test_man_child_dict(man: Manifest):
    cd = man._child_dict(TEST_KEY)
    assert cd
    assert isinstance(cd, dict)
    assert cd[man.kName] == [TEST_KEY]
    # assert cd[man.kPlaces] == [[TEST_OBJ]]
    # assert cd[man.kPath] == UPath(TEST_OBJ)
    assert cd[man.kSize] == [TEST_SIZE]
    hash = cd[man.kHash][0]
    assert isinstance(hash, dict)
    assert hash["value"] == TEST_OBJ_HASH
    assert hash["type"] == man.DEFAULT_HASH_TYPE


def test_man_entry(man: Manifest):
    entry = man.get(TEST_KEY)
    assert entry
    assert isinstance(entry, Entry)
    assert entry.args


def test_man_list(man: Manifest):
    results = man.list()
    assert len(results) == 1
    entry = results[0]
    assert isinstance(entry, Entry)
    assert TEST_KEY in str(entry.path)


def test_man_get(man: Manifest):
    entry = man.get(TEST_KEY)
    assert "manifest" in entry.args
    assert entry
    assert isinstance(entry, Entry)
    assert TEST_KEY in str(entry.path)
    # TODO: assert entry.version == TEST_VER
