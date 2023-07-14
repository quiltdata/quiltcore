from pytest import fixture
from quiltcore import Entry, Registry, Spec
from upath import UPath

NEW_PRK = "spec/quiltcore"

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
    - file-level metadata
    - package hash (verify)
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
        opts = entry.read_opts()
        assert opts
        assert entry.KEY_S3VER in opts
        assert entry.to_text() == value


def test_spec_write():
    """
    Ensure quilt3 can read manifests created by quiltcore

    * create files and metadata
    * create package
    * write to bucket
    * track all of the above
    * read it all back
    * TODO: calculate / verify package hash
    """
    pass



def test_spec_workflow():
    """
    Ensure quiltcore enforces bucket workflows
    """
    pass
