import pytest  # noqa: F401

from datetime import date, datetime
from json import JSONEncoder
from tempfile import TemporaryDirectory

from pytest import fixture, skip
from quilt3 import Package  # type: ignore
from upath import UPath

from quiltcore import Entry2, Header, Spec
from quiltcore import Domain, Manifest2, UDI

from .conftest import LOCAL_ONLY

TIME_NOW = Domain.TimeStamp()
PKG_PARQUET = "spec/parquet"

if LOCAL_ONLY:
    skip(allow_module_level=True)


@fixture
def spec():
    return Spec()


@fixture
def udi(spec: Spec) -> UDI:
    return spec.udi()


@fixture  # (scope="session")
def q3pkg(spec: Spec) -> Package:
    return Package.browse(
        spec.namespace(), registry=spec.registry(), top_hash=spec.hash()
    )


@fixture
def man2(udi: UDI) -> Manifest2:
    return Domain.GetRemoteManifest(udi)


@fixture
def spec_new():
    return Spec(PKG_PARQUET, TIME_NOW)


@fixture
def tmpdir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


def test_spec(spec: Spec, q3pkg: Package, man2: Manifest2):
    assert spec
    assert isinstance(spec, Spec)
    assert "quilt" in Spec.CONFIG_FILE
    assert "s3://" in spec.registry()
    assert q3pkg
    assert isinstance(q3pkg, Package)
    assert man2
    assert isinstance(man2, Manifest2)


def test_spec_new(spec_new: Spec, spec: Spec):
    assert spec_new
    assert spec_new.registry() == spec.registry()
    assert spec_new.namespace() != spec.namespace()
    assert spec_new.namespace() == PKG_PARQUET

    update = spec_new.pkg("update")
    _files = spec_new.files()
    assert update in _files
    updated = _files[update]
    assert updated == spec_new.update
    assert updated == TIME_NOW

    udi = spec_new.udi_new()
    assert isinstance(udi, UDI)
    uri = udi.uri
    assert isinstance(uri, str)
    assert PKG_PARQUET in uri


def test_spec_hash(spec: Spec, q3pkg: Package, man2: Manifest2):
    """
    Verify quiltcore matches quilt3 hashing

    1. Objects to be hashed
    2. Encoding / concatenation
    3. Hashing
    """
    json_encode = JSONEncoder(sort_keys=True, separators=(",", ":")).encode

    assert q3pkg
    q3_hash = q3pkg.top_hash
    assert q3_hash == spec.hash(), "q3_hash != spec.hash()"
    top_hash = q3pkg._calculate_top_hash(q3pkg._meta, q3pkg.walk())
    assert q3_hash == top_hash, "q3_hash != pkg._calculate_top_hash()"
    head = man2.table().head
    man_meta = head.hashable_dict()
    pkg_user = q3pkg._meta[man2.K_USER_META]
    man_user = man_meta[man2.K_USER_META]
    assert pkg_user["Date"] == man_user["Date"]  # type: ignore
    assert q3pkg._meta == head.hashable_dict()
    encoded = json_encode(q3pkg._meta).encode()
    assert encoded == head.hashable()

    for part in q3pkg._get_top_hash_parts(q3pkg._meta, q3pkg.walk()):
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
        actual = head.user_meta[key]  # type: ignore
        print(f"{key} value:{value}@{type(value)} actual:{actual}@{type(actual)}")
        if isinstance(value, date) and isinstance(actual, datetime):
            actual = actual.date()
        if isinstance(value, date) and isinstance(actual, str):
            value = str(value)
        assert actual == value  # type: ignore

    for key, value in spec.files().items():
        entry = man2[key]
        assert entry.name in spec.files().keys()
        assert isinstance(entry, Entry2)
        assert hasattr(entry, entry.K_VER)
        actual = entry.path.read_text().strip()
        print(f"{key} value:{value} actual:{actual}")
        assert actual == value
        if hasattr(entry, entry.K_USER_META):
            meta = spec.metadata(key)
            assert meta
            assert entry.user_meta == meta  # type: ignore


@pytest.mark.skip(reason="TODO: check config")
def test_spec_write(spec_new: Spec, tmpdir: UPath):
    """
    Ensure quilt3 can read manifests created by quiltcore

    With QuiltCore:
    * create local and remote Domain
    * write files in local store
    * commit to local Manifest (with metadata)
    * push to remote

    Then with quilt3:
    * read it back
    * TBD: file-level metadata
    """

    # 1. Create Domains
    local = Domain.FromLocalPath(tmpdir)
    pkg_name = spec_new.namespace()

    # 2. Write Files
    folder = local.package_path(pkg_name)
    for filename, filedata in spec_new.files().items():
        path = folder / filename
        path.write_text(filedata)  # TODO: Object-level Metadata

    # 3. Commit Manifest to Local Domain
    msg = f"test_spec_write {TIME_NOW}"
    pkg_meta = {
        local.K_META: spec_new.metadata(),
        local.K_MESSAGE: msg,
        local.K_PACKAGE: pkg_name,
    }
    tag = local.commit(folder, **pkg_meta)
    assert tag
    ns = local[pkg_name]
    assert ns
    man = ns[tag]
    assert man

    # 4. Push to Remote Domain
    local.push(folder, remote=spec_new.udi_new())

    # 5. Read it back
    qpkg = Package.browse(spec_new.namespace(), registry=spec_new.registry())
    assert qpkg

    meta = qpkg._meta
    new_meta = local.cf.encode_dates(spec_new.metadata())
    assert meta
    assert meta[local.K_USER_META] == new_meta
    assert meta[local.K_MESSAGE] == msg

    for filename, filedata in spec_new.files().items():
        assert filename in qpkg
        entry = qpkg[filename]
        assert entry.deserialize() == filedata


@pytest.mark.skip(reason="TODO: implement workflows")
def test_spec_workflow():
    """Ensure quiltcore enforces bucket workflows"""
    pass


@pytest.mark.skip(reason="TODO: implement object-level metadata")
def test_spec_object_meta():
    """Ensure quiltcore enforces bucket workflows"""
    pass


@pytest.mark.skip(reason="TODO: test versioning")
def test_spec_version_id(spec: Spec):
    """
    Get two versioned place URIs
    Verify that we extract the proper version ID
    Retrieve their contents
    Ensure they differ, and match the spec
    Possibly reuse same mechanism to specify minio endpoints
    """
    pass
