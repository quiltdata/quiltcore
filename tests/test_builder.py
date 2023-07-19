from tempfile import TemporaryDirectory

from pytest import fixture, raises, mark
from quiltcore import Builder, Manifest
from upath import UPath


FILENAME = "filename.txt"
FILETEXT = "hello world"


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


@fixture
def build(dir: UPath) -> Builder:
    path = dir / FILENAME
    path.write_text(FILETEXT)
    hash = {
        'value': 'abc123',
        'type': Builder.DEFAULT_HASH_TYPE
    }
    row = {'name': 'foo', '_path': str(path), 'hash': [hash], 'meta': {'content': "context"}}
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
    assert build.head.version == 'v0'  # type: ignore
    assert build.head.message == build.cf.get('quilt3/headers/message')  # type: ignore
    assert build.head.user_meta == {}  # type: ignore
    bd = build.head.to_dict()
    print(bd)
    assert bd['user_meta'] == {}


def test_build_man(build: Builder):
    man = build.to_manifest()
    assert isinstance(man, Manifest)
    print(man.head.to_dict())
    assert man.head.to_dict() == build.head.to_dict()
    mlist = man.list()
    assert len(mlist) == 1