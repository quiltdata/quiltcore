from pytest import raises
from quiltcore import Changes, Delta, Entry

from .conftest import dir, fixture, UPath  # noqa: F401

FILENAME = "filename.txt"
FILETEXT = "hello world"


@fixture
def chg():
    return Changes()


@fixture
def infile(dir: UPath) -> UPath:  # noqa: F401
    path = dir / FILENAME
    path.write_text(FILETEXT)
    return path.resolve()


@fixture
def changed(chg: Changes, infile: UPath):
    chg.post(str(infile))
    return chg


def test_chg_dir(dir: UPath):  # noqa: F401
    chg = Changes(dir)
    assert chg.path == dir / Changes.MANIFEST_FILE


def test_chg_file(dir: UPath):  # noqa: F401
    outfile = dir / "outfile.json"
    chg = Changes(outfile)
    assert chg.path == outfile


def test_chg_infile(infile: UPath):
    assert infile.exists()


def test_chg_delta(infile: UPath):
    delta = Delta(infile)
    assert delta.path == infile
    assert delta.action == "add"
    assert delta.name == FILENAME
    p = delta.to_dict()
    assert p["name"] == FILENAME
    y = str(delta)
    assert f"name: {FILENAME}" in y


def test_chg_delta_rm(infile: UPath):
    delta = Delta(infile, action="rm", name="foo.md", prefix="bar/")
    assert delta.path == infile
    assert delta.action == "rm"
    assert delta.name == "bar/foo.md"


def test_chg_put(chg: Changes, infile: UPath):
    test_key = "largo"
    chg.post(str(infile), name=test_key)
    delta = chg.get_delta(test_key)
    assert delta.name == test_key

    chg.delete(test_key)
    with raises(KeyError):
        chg.get_delta(test_key)

    with raises(KeyError):
        chg.get("invalid_key")


def test_chg_get(changed: Changes):
    entry = changed.get(FILENAME)
    assert isinstance(entry, Entry)


def test_chg_list(changed: Changes):
    entries = changed.list()
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, Entry)
    assert entry.name == FILENAME


def test_chg_str(changed: Changes):
    y = str(changed)
    assert f"{FILENAME}:" in y
