from pathlib import Path
from quiltcore import CoreRegistry

def test_registry():
    reg = CoreRegistry(Path("."))
    assert reg
    assert reg.conf