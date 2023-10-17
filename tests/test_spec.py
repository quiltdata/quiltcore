from json import JSONEncoder
from tempfile import TemporaryDirectory

from pytest import fixture, skip
from quilt3 import Package  # type: ignore
from upath import UPath

from quiltcore import Builder, Changes, Entry, Header, Manifest, Registry, Spec, Volume
from quiltcore import Domain, Manifest2, UDI

from .conftest import LOCAL_ONLY

TIME_NOW = Registry.Now()

if LOCAL_ONLY:
    skip(allow_module_level=True)


@fixture
def spec():
    return Spec()


@fixture
def udi(spec: Spec) -> UDI:
    return spec.udi()


@fixture  # (scope="session")
def pkg(spec: Spec) -> Package:
    return Package.browse(
        spec.namespace(), registry=spec.registry(), top_hash=spec.hash()
    )


@fixture
def man(spec: Spec) -> Manifest:
    reg = Registry.AsPath(spec.registry())
    registry = Registry(reg)
    namespace = registry.getResource(spec.namespace())
    man = namespace.getResource(spec.tag())
    return man  # type: ignore


@fixture
def man2(udi: UDI) -> Manifest2:
    return Domain.GetRemoteManifest(udi)


@fixture
def spec_new():
    return Spec("spec/quiltcore", TIME_NOW)


@fixture
def tmpdir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


def test_spec(spec: Spec, pkg: Package, man2: Manifest2):
    assert spec
    assert isinstance(spec, Spec)
    assert "quilt" in Spec.CONFIG_FILE
    assert "s3://" in spec.registry()
    assert pkg
    assert isinstance(pkg, Package)
    assert man2
    assert isinstance(man2, Manifest2)


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


def test_spec_hash(spec: Spec, pkg: Package, man2: Manifest2):
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
    head = man2.table().head
    man_meta = head.hashable_dict()
    pkg_user = pkg._meta[man2.K_USER_META]
    man_user = man_meta[man2.K_USER_META]
    assert pkg_user["Date"] == man_user["Date"]  # type: ignore
    assert pkg._meta == head.hashable_dict()
    encoded = json_encode(pkg._meta).encode()
    assert encoded == head.hashable()

    for part in pkg._get_top_hash_parts(pkg._meta, pkg.walk()):
        if "logical_key" in part:
            key = part["logical_key"]
            entry = man2[key]
            hashable = entry.hashable_dict()  # type: ignore
            assert part == hashable
            part_encoded = json_encode(part).encode()
            assert part_encoded == entry.hashable()  # type: ignore
            encoded += part_encoded

    multihash = man2.digest_bytes(encoded)
    man_struct = man2.cf.encode_hash(multihash)
    assert q3_hash == man_struct["value"], "q3_hash != digest(encoded).removeprefix"
    assert q3_hash == man2.q3hash(), "q3_hash != man.hash_quilt3()"


def test_spec_read(spec: Spec, man2: Manifest2):
    """
    Ensure quiltcore can read manifests created by quilt3

    - physical key
    - package-level metadata
    - file-level metadata
    """
    head = man2.table().head
    assert isinstance(head, Header)
    assert hasattr(head, "user_meta")
    assert isinstance(head.user_meta, dict)  # type: ignore
    for key, value in spec.metadata().items():
        assert key in head.user_meta  # type: ignore
        assert head.user_meta[key] == value  # type: ignore

    for key, value in spec.files().items():
        entry = man2[key]
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

    # 1. Create Changes
    for filename, filedata in spec_new.files().items():
        path = tmpdir / filename
        path.write_text(filedata)  # TODO: Object-level Metadata

    chg = Changes(tmpdir)
    delta = chg.post(tmpdir)
    assert delta

    # 2. Create Manifest
    msg = f"test_spec_write {TIME_NOW}"
    pkg_meta = {
        chg.KEY_USER: spec_new.metadata(),
        chg.KEY_MSG: msg,
    }
    man = Builder.MakeManifest(chg, pkg_meta)
    assert man

    opts = {
        chg.KEY_FRC: True,
        chg.KEY_NS: spec_new.namespace(),
    }
    bkt = UPath(spec_new.registry())
    vol = Volume(bkt)
    vol.put(man, **opts)

    qpkg = Package.browse(spec_new.namespace(), registry=spec_new.registry())
    assert qpkg

    meta = qpkg._meta
    new_meta = man.codec.encode_dates(spec_new.metadata())
    assert meta
    assert meta["user_meta"] == new_meta
    assert meta[vol.KEY_MSG] == msg

    for filename, filedata in spec_new.files().items():
        assert filename in qpkg
        entry = qpkg[filename]
        assert entry.deserialize() == filedata


def test_spec_workflow():
    """
    Ensure quiltcore enforces bucket workflows
    """
    pass
