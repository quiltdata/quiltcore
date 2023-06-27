from pathlib import Path
from pytest import fixture
from quiltcore import CoreRegistry
from upath import UPath

from .conftest import TEST_BKT, TEST_PKG


@fixture
def reg():
    path_bkt = UPath(TEST_BKT)
    return CoreRegistry(path_bkt)

def test_registry(reg):
    assert reg
    assert reg.config
    assert TEST_BKT in str(reg.config)

def test_registry_list(reg):
    result = reg.list()
    assert isinstance(result, list)
    assert len(result) == 0