from pytest import fixture
from quiltcore import Entry, Manifest
from upath import UPath

from .conftest import TEST_KEY, TEST_OBJ, TEST_TABLE


@fixture
def man():
    path = UPath(TEST_TABLE)
    return Manifest(path)


def test_man(man: Manifest):
    assert man
    assert man.table
    assert man.version == "v0"  # type: ignore
    assert man.body.num_rows == 1


def test_man_list(man: Manifest):
    results = man.list()
    assert len(results) == 1
    entry = results[0]
    assert isinstance(entry, Entry)
    assert str(entry.path) in TEST_OBJ


def test_man_get(man: Manifest):
    entry = man.get(TEST_KEY)
    assert entry
    assert isinstance(entry, Entry)
    assert str(entry.path) in TEST_OBJ
    # TODO: assert result.version == TEST_VER
