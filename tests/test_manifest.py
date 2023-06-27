from quiltcore import CoreManifest
from upath import UPath

from .conftest import TEST_TABLE

def test_man():
    path = UPath(TEST_TABLE)
    man = CoreManifest.FromPath(path)
    assert man
    assert man.table
