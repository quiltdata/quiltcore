from json import JSONEncoder
from tempfile import TemporaryDirectory

from pytest import fixture, skip
from quilt3 import Package  # type: ignore
from quiltcore import Changes, Entry, Header, Manifest, Registry, Spec, Volume
from upath import UPath

from .conftest import LOCAL_ONLY

TIME_NOW = Registry.Now()

if LOCAL_ONLY:
    skip(allow_module_level=True)


@fixture  # (scope="session")
def spec():
    return Spec()


@fixture  # (scope="session")
def pkg(spec: Spec) -> Package:
    return Package.browse(
        spec.namespace(), registry=spec.registry(), top_hash=spec.hash()
    )


@fixture
def man(spec: Spec) -> Manifest:
    reg = Registry.AsPath(spec.registry())
    registry = Registry(reg)
    namespace = registry.get(spec.namespace())
    man = namespace.get(spec.tag())
    return man  # type: ignore


@fixture
def spec_new():
    return Spec("spec/quiltcore", TIME_NOW)


@fixture
def tmpdir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


def test_spec(spec: Spec, pkg: Package, man: Manifest):
    assert spec
    assert isinstance(spec, Spec)
    assert "quilt" in Spec.CONFIG_FILE
    assert "s3://" in spec.registry()
    assert pkg
    assert isinstance(pkg, Package)
    assert man
    assert isinstance(man, Manifest)


def test_spec_new(spec_new: Spec, spec: Spec):
    assert spec_new
    assert spec_new.registry() == spec.registry()
    assert spec_new.namespace() != spec.namespace()
    update = spec_new.pkg("update")
    _files = spec_new.files()
    assert update in _files
    updated = _files[update]
    assert updated == spec_new.update
    assert updated == TIME_NOW


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
    pkg_user = pkg._meta[man.KEY_USER]
    man_user = man_meta[man.KEY_USER]
    assert pkg_user["Date"] == man_user["Date"]  # type: ignore
    assert pkg._meta == man.head.to_hashable()
    encoded = json_encode(pkg._meta).encode()
    assert encoded == man.head.hashable()

    for part in pkg._get_top_hash_parts(pkg._meta, pkg.walk()):
        if "logical_key" in part:
            key = part["logical_key"]
            entry = man.get(key)
            hashable = entry.to_hashable()  # type: ignore
            assert part == hashable
            part_encoded = json_encode(part).encode()
            assert part_encoded == entry.hashable()  # type: ignore
            encoded += part_encoded

    multihash = man.digest(encoded)
    man_struct = man.codec.encode_hash(multihash)
    assert q3_hash == man_struct["value"], "q3_hash != digest(encoded).removeprefix"
    assert q3_hash == man.hash_quilt3(), "q3_hash != man.hash_quilt3()"


def test_spec_read(spec: Spec, man: Manifest):
    """
    Ensure quiltcore can read manifests created by quilt3

    - physical key
    - package-level metadata
    - file-level metadata
    """
    head = man.head
    assert head
    assert isinstance(head, Header)
    assert hasattr(head, "user_meta")
    assert isinstance(head.user_meta, dict)  # type: ignore
    for key, value in spec.metadata().items():
        assert key in head.user_meta  # type: ignore
        assert head.user_meta[key] == value  # type: ignore

    for key, value in spec.files().items():
        entry = man.get(key)
        assert entry
        assert entry.name in spec.files().keys()
        assert isinstance(entry, Entry)
        opts = entry.read_opts()
        assert opts
        assert entry.KEY_S3VER in opts
        assert entry.to_text() == value
        if hasattr(entry, "user_meta"):
            meta = spec.metadata(key)
            assert entry.user_meta == meta  # type: ignore


def test_spec_write(spec_new: Spec, tmpdir: UPath):
    """
    Ensure quilt3 can read manifests created by quiltcore

    With QuiltCore:
    * create files and metadata
    * create package
    * write to bucket
    * track all of the above

    Then with quilt3:
    * read it all back
    """
    for filename, filedata in spec_new.files().items():
        path = tmpdir / filename
        path.write_text(filedata) # TODO: Object-level Metadata

    chg = Changes(tmpdir)
    delta = chg.post(tmpdir)
    msg = f"test_spec_write {TIME_NOW}"
    opts = {chg.KEY_NS: spec_new.namespace(), chg.KEY_FRC: True, chg.KEY_MSG: msg}
    man = chg.to_manifest(**opts)  # TODO: user_meta=pkg_metadata
    assert delta
    assert man

    bkt = UPath(spec_new.registry())
    vol = Volume(bkt)
    vol.put(man, **opts)

    qpkg = Package.browse(spec_new.namespace(), registry=spec_new.registry())
    assert qpkg

    meta = qpkg._meta
    assert meta
    assert meta["user_meta"] == spec_new.metadata()  # type: ignore
    assert meta[vol.KEY_MSG] == msg

    for filename, filedata in spec_new.files().items():
        assert filename in qpkg
        assert qpkg[filename] == filedata


def test_spec_workflow():
    """
    Ensure quiltcore enforces bucket workflows
    """
    pass
