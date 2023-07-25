from tempfile import TemporaryDirectory

from pytest import fixture, raises
from quiltcore import Builder, Decoder, Manifest
from upath import UPath

FILENAME = "filename.txt"
FILETEXT = "hello world"


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def build(dir: UPath) -> Builder:
    """Why does row require a hash? And as a list?"""
    path = dir / FILENAME
    path.write_text(FILETEXT)
    row = {
        Decoder.K_NAM: FILENAME,
        Decoder.K_PLC: str(path),
        Builder.KEY_META: {"content": "context"},
    }
    return Builder(dir, [row])


def test_build(build: Builder):
    assert build
    assert build.path.exists()
    assert build.path.is_dir()


def test_build_raise(dir: UPath):
    with raises(KeyError):
        build = Builder(dir, [{}])
        assert build


def test_build_head(build: Builder):
    assert build.head
    assert build.head.version == "v0"  # type: ignore
    assert build.head.message == build.cf.get("quilt3/headers/message")  # type: ignore
    assert build.head.user_meta == {}  # type: ignore
    bd = build.head.to_dict()
    assert bd["user_meta"] == {}


def test_build_man(build: Builder):
    man = build.to_manifest()
    assert isinstance(man, Manifest)
    assert man.head.to_dict() == build.head.to_dict()

    mlist = man.list()
    assert len(mlist) == 1
    entry = mlist[0]
    assert entry.name == FILENAME

    hash = man.hash_quilt3()
    assert hash == man.name
