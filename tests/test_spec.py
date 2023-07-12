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
    assert isinstance(manifest, Manifest)
    assert hasattr(manifest, "user_meta")


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
