from pytest import fixture
from quiltcore import Spec
from quilt3 import Package  # type: ignore

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
    pass


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
