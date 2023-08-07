from tempfile import TemporaryDirectory

from pytest import fixture, raises
from quiltcore import Changes, Delta, Entry
from upath import UPath

from .conftest import MockChanges


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def chg(dir: UPath):
    return Changes(dir)


@fixture
def infile(dir: UPath) -> UPath:
    chg = MockChanges(dir)
    return chg.infile  # type: ignore


@fixture
def changed(dir: UPath):
    chg = MockChanges(dir)
    return chg


def test_chg(chg: Changes):
    assert chg is not None


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
    assert delta.name == MockChanges.FILENAME

    cn = delta._child_names()
    assert len(cn) == 1
    assert cn[0] == str(infile)

    cd = delta._child_dict(cn[0])
    assert cd[delta.cf.K_NAM] == MockChanges.FILENAME
    assert cd[delta.cf.K_PLC] == str(infile)

    entries = delta.list()
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry, Entry)
    assert entry.path == infile
    assert entry.name == MockChanges.FILENAME

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
    delta = changed.get(MockChanges.FILENAME)
    assert isinstance(delta, Delta)


def test_chg_list(changed: Changes):
    deltas = changed.list()
    assert len(deltas) == 1
    delta = deltas[0]
    assert isinstance(delta, Delta)
    assert delta.name == MockChanges.FILENAME


def test_chg_str(changed: Changes):
    y = str(changed)
    assert f"{MockChanges.FILENAME}:" in y
