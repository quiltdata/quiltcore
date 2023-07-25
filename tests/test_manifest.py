from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import fixture
from quiltcore import Entry, Header, Manifest, Registry

from .conftest import (
    TEST_KEY, TEST_MAN, TEST_OBJ, TEST_S3VER, TEST_SIZE, TEST_VER, TEST_VOL
)

@fixture
def opts() -> dict:
    root = TEST_VOL
    rootdir = Path(root)
    opts = {Registry.ARG_REG: Registry(rootdir)}
    return opts


@fixture
def man(opts: dict) -> Manifest:
    path = Manifest.AsPath(TEST_MAN)
    return Manifest(path, **opts)


def test_man(man: Manifest):
    assert man
    assert man.table
    assert "manifest" in man.args


def test_man_head(man: Manifest):
    head = man.head
    assert head
    assert isinstance(head, Header)

    hashable = head.to_hashable()
    assert hashable
    assert isinstance(hashable, dict)
    assert hashable["user_meta"]["Author"] == "Ernest"


def test_man_child_place(man: Manifest):
    assert Registry.ARG_REG in man.args
    plc = "./manual/force/ONLYME.md"
    place = man._child_place(plc)
    assert place != plc
    assert f"{place}?versionId={TEST_VER}" == TEST_OBJ
    
    
def test_man_child_dict(man: Manifest):
    cd = man._child_dict(TEST_KEY)
    assert cd
    print(cd)
    assert isinstance(cd, dict)
    assert cd[man.cf.K_NAM] == TEST_KEY
    assert cd[man.KEY_SZ] == TEST_SIZE
    mhash = cd[man.KEY_MH]
    assert isinstance(mhash, str)
    #assert cd[man.cf.K_PLC] == TEST_OBJ
    #assert cd[man.KEY_S3VER] == TEST_S3VER


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
    # TODO: assert entry.version == TEST_VER


def test_man_hash(man: Manifest):
    hash = man.hash_quilt3()
    assert hash == man.name
