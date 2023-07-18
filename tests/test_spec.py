from json import JSONEncoder

from pytest import fixture
from quilt3 import Package  # type: ignore
from quiltcore import Entry, Header, Manifest, Registry, Spec
from upath import UPath

NEW_PRK = "spec/quiltcore"


@fixture
def spec():
    return Spec()


@fixture
def pkg(spec: Spec) -> Package:
    return Package.browse(
        spec.namespace(), registry=spec.registry(), top_hash=spec.hash()
    )


@fixture
def man(spec: Spec) -> Manifest:
    reg = UPath(spec.registry())
    registry = Registry(reg)
    namespace = registry.get(spec.namespace())
    manifest = namespace.get(spec.tag())
    return manifest  # type: ignore


def test_spec(spec: Spec, pkg: Package, man: Manifest):
    assert spec
    assert isinstance(spec, Spec)
    assert "quilt" in Spec.CONFIG_FILE
    assert "s3://" in spec.registry()
    assert pkg
    assert man


def test_spec_hash(spec: Spec, pkg: Package, man: Manifest):
    """
    Verify quiltcore matches quilt3 hashing

    1. Objects to be hashed
    2. Encoding / concatenation
    3. Hashing
    """
    json_encode = JSONEncoder(sort_keys=True, separators=(",", ":")).encode

    assert pkg
    q3_hash = pkg.top_hash
    assert q3_hash == spec.hash(), "q3_hash != spec.hash()"
    assert q3_hash == pkg._calculate_top_hash(
        pkg._meta, pkg.walk()
    ), "q3_hash != pkg._calculate_top_hash()"

    man_meta = man.head.to_hashable()
    pkg_user = pkg._meta[man.kMeta]
    man_user = man_meta[man.kMeta]
    assert pkg_user["Date"] == man_user["Date"]  # type: ignore
    assert pkg._meta == man.head.to_hashable()
    encoded = json_encode(pkg._meta).encode()
    assert encoded == man.head.hashable()

    for part in pkg._get_top_hash_parts(pkg._meta, pkg.walk()):
        print(f"part: {part}")
        if "logical_key" in part:
            key = part["logical_key"]
            entry = man.get(key)
            hashable = entry.to_hashable()  # type: ignore
            print(f"entry[{key}]: {hashable}")
            assert part == hashable
            part_encoded = json_encode(part).encode()
            assert part_encoded == entry.hashable()  # type: ignore
            encoded += part_encoded

    man_encoded = man.digest(encoded)
    man_strip = man_encoded.removeprefix(Manifest.DEFAULT_MH_PREFIX)
    assert q3_hash == man_strip, "q3_hash != digest(encoded).removeprefix"
    assert q3_hash == man.calc_hash(), "q3_hash != man.calc_hash()"


def test_spec_read(spec: Spec, man: Manifest):
    """
    Ensure quiltcore can read manifests created by quilt3

    - physical key
    - package-level metadata
    - file-level metadata
    - package hash (verify)
    """
    manifest = man
    assert manifest
    assert isinstance(manifest, Manifest)
    head = manifest.head
    assert head
    assert isinstance(head, Header)
    assert hasattr(head, "user_meta")
    assert isinstance(head.user_meta, dict)  # type: ignore
    for key, value in spec.metadata().items():
        assert key in head.user_meta  # type: ignore
        assert head.user_meta[key] == value  # type: ignore

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
