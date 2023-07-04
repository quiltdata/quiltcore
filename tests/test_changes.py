from pytest import fixture, raises
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


def test_chg_dir(dir: UPath):
    chg = Changes(dir)
    assert chg.path == dir / Changes.MANIFEST_FILE


def test_chg_file(dir: UPath):
    outfile = dir / "outfile.json"
    chg = Changes(outfile)
    assert chg.path == outfile


def test_chg_infile(infile: UPath):
    assert infile.exists()


def test_chg_delta(infile: UPath):
    delta = Delta(infile)
    assert delta.path == infile
    assert delta.action == "add"
    assert delta.key == FILENAME


def test_chg_delta_rm(infile: UPath):
    delta = Delta(infile, action="rm", key="foo.md", prefix="bar/")
    assert delta.path == infile
    assert delta.action == "rm"
    assert delta.key == "bar/foo.md"


def test_chg_put(chg: Changes, infile: UPath):
    test_key = "largo"
    chg.put(infile, key=test_key)
    delta = chg.get_delta(test_key)
    assert delta.key == test_key

    chg.delete(test_key)
    with raises(KeyError):
        chg.get_delta(test_key)

    with raises(KeyError):
        chg.get("invalid_key")

def test_chg_deltas(chg: Changes, infile: UPath):
    chg.put(infile)
    deltas = chg.list_deltas()
    assert len(deltas) == 1
    rsrc = deltas[0]
    assert isinstance(rsrc, Delta)
    assert rsrc.key == FILENAME
