from multiformats import multihash
from pytest import fixture
from quiltcore import CoreBlob, CoreManifest
from tempfile import TemporaryDirectory
from upath import UPath

from .conftest import TEST_TABLE, TEST_KEY, TEST_OBJ_HASH, TEST_OBJ

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
    # TODO: assert result.version == TEST_VER


def test_blob(man: CoreManifest):
    blob: CoreBlob = man.get(TEST_KEY)  # type: ignore
    assert isinstance(blob.parent, CoreManifest)
    assert blob.logical_key == TEST_KEY  # type: ignore
    assert blob.physical_key == TEST_OBJ  # type: ignore
    assert blob.hash["value"] == TEST_OBJ_HASH  # type: ignore
    assert blob.hash["type"] == "SHA256"  # type: ignore
    assert blob.size == 100764599  # type: ignore

    assert blob.hash_value == TEST_OBJ_HASH
    assert blob.hash_type == "sha2-256"

    meta = blob.meta  # type: ignore
    assert meta
    assert isinstance(meta, dict)
    assert meta["target"] == 'parquet'


def test_blob_put(man: CoreManifest):
    blob = man.get(TEST_KEY)
    with TemporaryDirectory() as tmpdirname:
        dest = UPath(tmpdirname) / TEST_KEY
        loc = blob.put(dest)
        print(loc)
        assert TEST_KEY in str(loc)
        assert loc.exists()


def test_blob_verify(man: CoreManifest):
    blob = man.get(TEST_KEY)

