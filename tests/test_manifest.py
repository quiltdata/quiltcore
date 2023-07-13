from pytest import fixture
from quiltcore import Entry, Manifest

from .conftest import TEST_KEY, TEST_OBJ_HASH, TEST_SIZE, TEST_TABLE


@fixture
def man():
    path = Manifest.AsPath(TEST_TABLE)
    return Manifest(path)


def test_man_headers(man: Manifest):
    assert man
    assert man.version == "v0"  # type: ignore
    assert len(man.message) > 0  # type: ignore
    assert len(man.user_meta) > 0  # type: ignore
    assert man.user_meta["Author"] == "Ernest"  # type: ignore
    assert "manifest" in man.args


def test_man_table(man: Manifest):
    assert man.table
    assert man.body
    assert man.body.num_rows == 1
    schema = man.body.schema
    assert schema
    columns = man.cf.get_dict("quilt3/columns")
    for key in columns:
        assert key in schema.names

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
