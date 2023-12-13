from tempfile import TemporaryDirectory
from pathlib import Path
import os
import pytest

from quiltcore import UDI, Domain, Manifest, Scheme, quilt

from .conftest import LOCAL_UDI, LOCAL_URI, LOCAL_VOL, TEST_HASH, TEST_PKG, not_win

MESSAGE = f"Hello World {Domain.Now()}"
TEST_FILE = "README.md"
TEST_META = {"key": "value"}


def FirstFile(path):
    return next(path.iterdir())


def make_domain():
    with TemporaryDirectory() as tmpdirname:
        f = quilt["file"]
        dom = f[tmpdirname]
        yield dom


@pytest.fixture
def domain():
    for dom in make_domain():
        yield dom


@pytest.fixture
def remote_udi():
    return UDI.FromUri(LOCAL_UDI)


@pytest.fixture
def committed():
    for local in make_domain():
        local_path = local.package_path(TEST_PKG)
        assert ".quilt" not in local_path.parents
        assert local_path.exists()
        readme = local_path / TEST_FILE
        readme.write_text(MESSAGE)
        assert readme.exists()
        assert MESSAGE in readme.read_text()
        kwargs = {
            Domain.K_META: TEST_META,
            Domain.K_MESSAGE: MESSAGE,
            Domain.K_PACKAGE: TEST_PKG,
        }
        local.commit(local_path, **kwargs)
        yield local


def test_dom_udi_scheme():
    assert "quilt+file://" in LOCAL_UDI
    f = quilt["file"]
    dom = f[LOCAL_VOL]
    assert isinstance(dom, Domain)
    assert isinstance(dom.parent, Scheme)
    assert LOCAL_VOL in dom.cf.AsString(dom.store)


def test_dom_remote_udi(remote_udi: UDI):
    assert remote_udi
    assert remote_udi.uri == LOCAL_UDI
    assert remote_udi.package == TEST_PKG
    if not_win():
        assert remote_udi.registry == LOCAL_URI


def test_dom_uri(domain: Domain):
    uri = domain.get_uri()
    assert uri.startswith("file:///")
    domain2 = Domain.FromURI(uri)
    assert domain2.store == domain.store


def test_dom_udi(domain: Domain):
    udi = domain.get_udi_string()
    assert udi.startswith("quilt+file:///")
    udip = domain.get_udi_string(TEST_PKG)
    assert udip.endswith(f"#package={TEST_PKG}")
    udipp = domain.get_udi_string(TEST_PKG, "README.md")
    assert udipp.endswith(f"#package={TEST_PKG}&path=README.md")


def test_dom_raise(domain: Domain, remote_udi: UDI):
    domain.is_mutable = False
    with pytest.raises(AssertionError):
        domain.pull(remote_udi, dest=None)


def test_dom_data_yaml(domain: Domain, remote_udi: UDI):
    dy = domain.data_yaml
    assert dy
    assert dy.path
    assert not dy.path.exists()
    path = domain.pull(remote_udi, hash=TEST_HASH)
    assert dy.path.exists()

    dest = str(path)
    assert TEST_PKG in dest
    assert dy.folder2uri(dest) == LOCAL_UDI
    assert dy.uri2folder(LOCAL_UDI) == dest

    status = dy.get_list(dest, LOCAL_UDI, "pull")
    assert isinstance(status, dict)
    assert "timestamp" in status
    assert "user" in status
    assert status["hash"] == TEST_HASH


def test_dom_get(domain: Domain):
    ns = domain[TEST_PKG]
    assert ns is not None
    assert not ns.path.exists()
    assert not domain

    ns.path.mkdir(parents=True, exist_ok=True)
    assert domain
    assert len(domain) == 1
    assert TEST_PKG in domain.keys()


def test_dom_build(committed: Domain):
    local_path = committed.package_path(TEST_PKG)
    builder = committed.build(local_path)
    assert builder


def test_dom_commit(committed: Domain):
    assert committed.path.exists()
    assert isinstance(committed, Domain)
    assert len(committed) == 1
    assert TEST_PKG in committed

    namespace = committed[TEST_PKG]
    assert len(namespace) == 2

    man = namespace[committed.TAG_DEFAULT]
    assert isinstance(man, Manifest)
    assert len(man) == 2
    assert TEST_FILE in man

    entry = man[TEST_FILE]
    assert entry.name == TEST_FILE
    assert entry.path.exists()
    assert entry.path.is_absolute()
    assert MESSAGE in entry.path.read_text()

    table = man.table()
    assert len(table) == 2
    assert table.head.info["message"] == MESSAGE
    assert table.head.meta == TEST_META


def test_dom_meta(domain):
    n_mega = os.environ.get("N_MEGA")
    dest = os.environ.get("DEST")
    N_MEGA = 100 if not n_mega else int(n_mega)
    MEGA_PKG = "manual/mega"
    mega = {str(i): i for i in range(N_MEGA)}
    kwargs = {
        Domain.K_META: {"mega": mega},
        Domain.K_MESSAGE: "test_dom_meta",
        Domain.K_PACKAGE: MEGA_PKG,
    }
    local_path = domain.package_path(MEGA_PKG)
    domain.commit(local_path, **kwargs)
    assert MEGA_PKG in domain
    pkg = domain[MEGA_PKG][domain.TAG_DEFAULT]
    assert pkg.path.exists()
    if dest:
        dest_path = Path(dest) / pkg.path.name
        contents = pkg.path.read_text()
        dest_path.write_text(contents)


def test_dom_unpull(committed: Domain):
    source_udi = committed.get_udi(TEST_PKG)
    print(source_udi)
    for local in make_domain():
        local.pull(source_udi)
        assert TEST_PKG in local
        local_path = local.package_path(TEST_PKG)
        print(local_path)
        first = FirstFile(local_path)
        assert local_path.exists()
        assert local_path.is_dir()
        assert TEST_FILE in str(first)
        assert MESSAGE in first.read_text()


def test_dom_push(committed: Domain):
    local_path = committed.package_path(TEST_PKG)
    assert local_path.exists()
    first = FirstFile(local_path)
    assert TEST_FILE in str(first)
    assert MESSAGE in first.read_text()

    for remote in make_domain():
        remote_udi = remote.get_udi(TEST_PKG)
        assert isinstance(remote, Domain)
        assert remote_udi
        committed.push(local_path, remote=remote_udi)
        # read it back
        remote_path = remote.package_path(TEST_PKG)
        assert remote_path.exists()
        remote_readme = remote_path / "README.md"
        assert remote_readme.exists()
        assert remote_readme.read_text() == MESSAGE
