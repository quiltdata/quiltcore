from pytest import fixture
from quiltcore import Entry, Manifest, Namespace, Registry, Resource, Spec, Volume
from quilt3 import Package  # type: ignore
from upath import UPath

@fixture
def spec():
    return Spec()

def test_spec(spec: Spec):
    assert spec
    assert isinstance(spec, Spec)
    assert "quilt" in Spec.CONFIG_FILE
    assert "s3://" in spec.registry()

def test_spec_read(spec: Spec):
    """
    Ensure quiltcore can read manifests created by quilt3
    
    - physical key
    - package-level metadata
    """
    reg = UPath(spec.registry())
    registry = Registry(reg)
    namespace = registry.get(spec.namespace())
    manifest = namespace.get(spec.tag())
    assert manifest
    assert hasattr(manifest, "user_meta")
    assert isinstance(manifest.user_meta, dict)  # type: ignore
    for key, value in spec.metadata().items():
        assert key in manifest.user_meta  # type: ignore
        assert manifest.user_meta[key] == value  # type: ignore

    for key, value in spec.files().items():
        entry = manifest.get(key)
        assert entry
        assert isinstance(entry, Entry)
        #assert entry.path.read_text() == value


def test_spec_write():
    """Ensure quilt3 can read manifests created by quiltcore"""
    pass


def test_spec_verify():
    """Ensure quilt3 can verify manifests created by quiltcore"""


def test_spec_workflow():
    """
    Ensure quiltcore enforces bucket workflows
    """
    pass
