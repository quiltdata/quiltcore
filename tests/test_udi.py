import pytest
import yaml
from pathlib import Path
from tempfile import TemporaryDirectory

from quiltcore import UDI

from .conftest import BKT_URI, PTH_URI, T_BKT, T_PKG, TEST_URI, LOCAL_UDI


@pytest.fixture
def udi():
    return UDI.FromUri(TEST_URI)


def test_udi(udi: UDI):
    assert udi.uri == TEST_URI
    assert udi.registry == f"s3://{T_BKT}"
    assert udi.package == T_PKG


def test_udi_repr(udi: UDI):
    assert TEST_URI in repr(udi)
    assert udi == udi


def test_udi_eq(udi: UDI):
    assert udi == udi
    udi_pth = UDI.FromUri(PTH_URI)
    assert udi_pth == udi
    udi_bkt = UDI.FromUri(BKT_URI)
    assert udi_bkt != udi


def test_udi_null():
    un = UDI({})
    assert un
    assert un.uri is None


def test_udi_localhost():
    local = UDI.FromUri(LOCAL_UDI)
    assert local
    assert local.uri == LOCAL_UDI
    assert "localhost" not in local.registry


def test_udi_dump_yaml(udi: UDI):
    with TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        tmpfile = tmpdir / "udi.yaml"
        yaml.safe_dump(udi, tmpfile.open("w"))
        print("test_udi_dump_yaml", tmpfile.read_text())
        udi2 = yaml.safe_load(tmpfile.open("r"))
        assert udi == udi2
