from tempfile import TemporaryDirectory

from pytest import fixture
from quiltcore import Builder, Manifest
from upath import UPath

from .test_changes import MockChanges

OPTS = {
    Builder.KEY_USER: {"key": "value"},
    Builder.KEY_MSG: "Test message",
}


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def build(dir: UPath) -> Builder:
    chg = MockChanges(dir)
    builder = Builder(chg)
    return builder


def test_build(build: Builder):
    assert build
    assert build.path.exists()
    assert build.path.is_dir()


def test_build_head(build: Builder):
    assert build.head
    assert build.head.version == "v0"  # type: ignore
    assert build.head.message == build.cf.get("quilt3/headers/message")  # type: ignore
    assert build.head.user_meta == {}  # type: ignore
    bd = build.head.to_dict()
    assert bd["user_meta"] == {}


def test_build_entries(build: Builder):
    entries = build.list()
    assert len(entries) == 1
    entry = entries[0]
    assert entry.name == MockChanges.FILENAME
    assert build.get(entry.name) == entry


def test_build_opts(dir: UPath):
    chg = MockChanges(dir)
    build = Builder(chg, **OPTS)
    assert build.head.version == "v0"  # type: ignore
    assert build.head.message == OPTS["message"]  # type: ignore
    assert build.head.user_meta == OPTS["user_meta"]  # type: ignore


def test_build_man(build: Builder):
    man = build.post(build.path)
    assert isinstance(man, Manifest)
    assert man.head().to_dict() == build.head.to_dict()

    mlist = man.list()
    assert len(mlist) == 1
    entry = mlist[0]
    assert entry.name == MockChanges.FILENAME

    hash = man.hash_quilt3()
    assert hash == man.name
