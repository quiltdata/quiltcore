from pytest import fixture, mark
from quiltcore import Codec, Entry, Header, Manifest, Registry
from upath import UPath

from .conftest import (
    LOCAL_ONLY,
    TEST_KEY,
    TEST_MAN,
    TEST_OBJ,
    TEST_S3VER,
    TEST_SIZE,
    TEST_VER,
    TEST_VOL,
    not_win,
)


@fixture
def opts() -> dict:
    root = TEST_VOL
    rootdir = UPath(root)
    opts = {Registry.ARG_REG: Registry(rootdir)}
    return opts


@fixture
def man(opts: dict) -> Manifest:
    path = Manifest.AsPath(TEST_MAN)
    return Manifest(path, **opts)


def test_man(man: Manifest):
    assert man
    assert man._table
    assert "manifest" in man.args


def test_man_head(man: Manifest):
    head = man.head()
    assert head
    assert isinstance(head, Header)

    hashable = head.to_hashable()
    assert hashable
    assert isinstance(hashable, dict)
    assert hashable["user_meta"]["Author"] == "Ernest"


@mark.skipif(LOCAL_ONLY, reason="skip network tests")
def test_man_version(man: Manifest):
    path = UPath(TEST_S3VER)
    version = Codec.StatVersion(path)
    assert version

    bad_path = UPath(TEST_OBJ)
    bad_version = Codec.StatVersion(bad_path)
    assert not bad_version


def test_man_child_place(man: Manifest):
    assert Registry.ARG_REG in man.args
    plc = "./manual/force/ONLYME.md"
    place = man._child_place(plc)
    assert place != plc
    if not_win():
        assert f"{place}?versionId={TEST_VER}" == TEST_OBJ


def test_man_child_dict(man: Manifest):
    cd = man._child_dict(TEST_KEY)
    assert cd
    assert isinstance(cd, dict)
    assert cd[man.cf.K_NAM] == TEST_KEY
    assert cd[man.KEY_SZ] == TEST_SIZE
    mhash = cd[man.KEY_MH]
    assert isinstance(mhash, str)


def test_man_entry(man: Manifest):
    entry = man.get(TEST_KEY)
    assert entry
    assert isinstance(entry, Entry)
    assert entry.args


def test_man_list(man: Manifest):
    results = man.list()
    assert len(results) == 1
    entry = results[0]
    assert isinstance(entry, Entry)
    assert TEST_KEY in str(entry.path)


def test_man_get(man: Manifest):
    entry = man.get(TEST_KEY)
    assert "manifest" in entry.args
    assert entry
    assert isinstance(entry, Entry)
    assert TEST_KEY in str(entry.path)


def test_man_hash(man: Manifest):
    hash = man.hash_quilt3()
    assert hash == man.name
