from tempfile import TemporaryDirectory

from pytest import fixture, raises
from quiltcore import Changes, Delta, Entry
from upath import UPath

FILENAME = "filename.txt"
FILETEXT = "hello world"


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def chg(dir: UPath):
    return Changes(dir)


@fixture
def infile(dir: UPath) -> UPath:
    path = dir / FILENAME
    path.write_text(FILETEXT)
    return path.resolve()


@fixture
def changed(chg: Changes, infile: UPath):
    chg.post(infile)
    return chg


def test_chg(chg: Changes):
    assert chg


def test_chg_dir(dir: UPath):
    chg = Changes(dir)
    assert chg.path == dir


def test_chg_file(dir: UPath):
    outfile = dir / "outfile.json"
    with raises(ValueError):
        Changes(outfile)


def test_chg_infile(infile: UPath):
    assert infile.exists()


def test_chg_delta(infile: UPath):
    delta = Delta(infile)
    assert delta.path == infile
    assert delta.action == "add"
    assert delta.name == FILENAME

    cn = delta._child_names()
    assert len(cn) == 1
    assert cn[0] == str(infile)

    cd = delta._child_dict(cn[0])
    assert cd[delta.cf.K_NAM] == FILENAME
    assert cd[delta.cf.K_PLC] == str(infile)

    entries = delta.list()
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, Entry)
    assert entry.path == infile
    assert entry.name == FILENAME

    delta_dir = Delta(infile.parent)
    assert entry == delta_dir.list()[0]


def test_chg_delta_rm(infile: UPath):
    delta = Delta(infile, action="rm", name="foo.md", prefix="bar/")
    assert delta.path == infile
    assert delta.action == "rm"
    assert delta.name == "bar/foo.md"

    entries = delta.list()
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, Entry)
    assert entry.meta == {Delta.KEY_RM: True}


def test_chg_post(chg: Changes, infile: UPath):
    test_key = "largo"
    delta = chg.post(infile, name=test_key)
    assert delta.name == test_key
    assert delta == chg.get(test_key)

    chg.delete(test_key)
    with raises(KeyError):
        chg.get(test_key)

    with raises(KeyError):
        chg.get("invalid_key")


def test_chg_get(changed: Changes):
    delta = changed.get(FILENAME)
    assert isinstance(delta, Delta)


def test_chg_list(changed: Changes):
    deltas = changed.list()
    assert len(deltas) == 1
    delta = deltas[0]
    assert isinstance(delta, Delta)
    assert delta.name == FILENAME


def test_chg_str(changed: Changes):
    y = str(changed)
    assert f"{FILENAME}:" in y


def test_chg_man_dir(chg: Changes):
    subdir = chg.path / "subdir"
    subdir.mkdir()
    subfile = subdir / FILENAME
    subfile.write_text(FILETEXT)
    chg.post(subdir)
