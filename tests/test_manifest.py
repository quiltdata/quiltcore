from pytest import fixture
from quiltcore import CoreManifest
from upath import UPath

from .conftest import TEST_TABLE

@fixture
def man():
    path = UPath(TEST_TABLE)
    return CoreManifest(path)

def test_man(man: CoreManifest):
    assert man
    assert man.table
    assert man.version == "v0"  # type: ignore
    assert man.body.num_rows == 1


def test_man_list(man: CoreManifest):
    results = man.list()
    assert len(results) == 1
    assert results == ["camera-reviews"]