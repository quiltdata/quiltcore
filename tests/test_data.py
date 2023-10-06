from tempfile import TemporaryDirectory

from pytest import fixture
from quiltcore import Data
from upath import UPath


@fixture
def data():
    with TemporaryDirectory() as tmpdirname:
        path = UPath(tmpdirname)
        yield Data(path)


def test_data(data: Data):
    assert data


def test_data_saves(data: Data):
    assert not data.path.exists()
    data.save()
    assert data.path.exists()


def test_data_put_list(data: Data):
    data.put_list("foo", "bar", "baz")
    data.save()
    assert data.get("foo/bar") == "baz"


def test_data_get_list(data: Data):
    data.put_list("foo", "bar", "baz")
    data.save()
    assert data.get_list("foo", "bar") == "baz"


def test_data_set(data: Data):
    status = {"time": "now", "user": "me"}
    data.set("folder", "uri", "action", status)
    data.save()
    assert data.get("folder/uri/action") == status
    assert data.get("folder/uri") == {"action": status}
    assert data.get_uri("folder") == "uri"
    assert data.get_folder("uri") == "folder"
