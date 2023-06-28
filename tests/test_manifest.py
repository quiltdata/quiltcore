from pytest import fixture
from quiltcore import CoreBlob, CoreManifest
from tempfile import TemporaryDirectory
from upath import UPath

from .conftest import TEST_TABLE, TEST_KEY, TEST_VER, TEST_OBJ

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
    blob = results[0]
    assert isinstance(blob, CoreBlob)
    assert str(blob.path) in TEST_OBJ

def test_man_get(man: CoreManifest):
    blob = man.get(TEST_KEY)
    assert blob
    assert isinstance(blob, CoreBlob)
    assert str(blob.path) in TEST_OBJ
    # TODO: assert result.version == TEST_VER  # type: ignore

def test_blob(man: CoreManifest):
    blob = man.get(TEST_KEY)
    assert isinstance(blob.parent, CoreManifest)

def test_blob_put(man: CoreManifest):
    blob = man.get(TEST_KEY)
    with TemporaryDirectory() as tmpdirname:
        dest = UPath(tmpdirname) / TEST_KEY
        loc = blob.put(dest)
        print(loc)
        assert TEST_KEY in str(loc)
        assert loc.exists()

