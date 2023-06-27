from pathlib import Path
from pytest import fixture, mark
from quiltcore import CoreRegistry
from upath import UPath

from .conftest import TEST_BKT, TEST_PKG

pytestmark = mark.anyio

@fixture
def reg():
    path_bkt = UPath(TEST_BKT)
    return CoreRegistry(path_bkt)

def test_registry(reg):
    assert reg
    assert reg.config
    assert TEST_BKT in str(reg.config)
    assert '.quilt/named_packages' in str(reg.names)
    assert '.quilt/packages' in str(reg.versions)
    assert reg.versions.exists()
    assert reg.names.is_dir()

async def test_registry_list(reg):
    result = await reg.list()
    assert isinstance(result, list)
    assert len(result) > 0
    assert TEST_PKG in str(result[0])