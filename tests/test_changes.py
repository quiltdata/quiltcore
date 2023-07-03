from pytest import fixture
from quiltcore import Changes, Delta, Manifest
from tempfile import TemporaryDirectory
from upath import UPath

# from .conftest import TEST_BKT, TEST_HASH, TEST_PKG, TEST_TAG

FILENAME = "filename.txt"
FILETEXT = "hello world"


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)

@fixture
def chg():
    return Changes()

@fixture
def infile(dir: UPath) -> UPath:
    path = dir / FILENAME
    path.write_text(FILETEXT)
    return path

def test_chg_infile(infile: UPath):
    assert infile.exists()

def test_chg_delta(infile: UPath):
    delta = Delta(infile)
    assert delta.path == infile
    assert delta.action == "add"
    assert delta.key == FILENAME

