from tempfile import TemporaryDirectory

from pytest import fixture
from quiltcore import CoreBlob, CoreManifest
from upath import UPath

from .conftest import TEST_KEY, TEST_OBJ, TEST_OBJ_HASH, TEST_TABLE

DATA_HW = b"Hello world!"
HASH_HW = "c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a"
# w/o 1220 prefix


@fixture
def blob():
    path = UPath(TEST_TABLE)
    man = CoreManifest(path)
    blob: CoreBlob = man.get(TEST_KEY)  # type: ignore
    return blob


def test_blob(blob: CoreBlob):
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
    assert meta["target"] == "parquet"


def test_blob_put(blob: CoreBlob):
    with TemporaryDirectory() as tmpdirname:
        dest = UPath(tmpdirname) / TEST_KEY
        loc = blob.put(dest)
        print(loc)
        assert TEST_KEY in str(loc)
        assert loc.exists()


def test_blob_digest(blob: CoreBlob):
    assert blob.hash_digest
    digest = blob.hash_digest.digest(DATA_HW)
    assert digest.hex() == CoreBlob.MH_PREFIX + HASH_HW

    digest2 = blob.digest(DATA_HW)
    assert digest2 == HASH_HW


def test_blob_digest_verify(blob: CoreBlob):
    blob.hash_value = HASH_HW
    assert blob.verify(DATA_HW)


def test_blob_verify(blob: CoreBlob):
    assert blob.hash_value
    with TemporaryDirectory() as tmpdirname:
        dest = UPath(tmpdirname) / TEST_KEY
        blob.put(dest)
        assert dest.exists()
        bstring = dest.read_bytes()
        assert blob.verify(bstring)
