from pathlib import Path
from tempfile import TemporaryDirectory

from pytest import fixture
from upath import UPath


@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


TEST_BKT = "s3://udp-spec"
LOCAL_VOL = "tests/example"

TEST_VOL = (Path.cwd() / LOCAL_VOL).as_uri()
TEST_PKG = "manual/force"
TEST_TAG = "1680720965"
TEST_HASH = "3210f808ac0467726439191eea3bd0a66ab261122ee55758367620fedc77fe08"
TEST_SIZE = 30
TEST_KEY = "ONLYME.md"
TEST_VER = "VetrR_Vukeiiv.NkXZXpQFKEibsK0QW3"
TEST_OBJ = f"{TEST_VOL}/{TEST_PKG}/{TEST_KEY}?versionId={TEST_VER}"
TEST_OBJ_HASH = "df3e419dfd21f653651a5131e17bf41d82a9fd72baf2a93f634773353bd9d6c8"

TEST_MAN = f"{TEST_VOL}/.quilt/packages/{TEST_HASH}"
TEST_S3VER = f"{TEST_BKT}/{TEST_PKG}/{TEST_KEY}?versionId={TEST_VER}"

TEST_ROW = {
    "logical_key": [TEST_KEY],
    "physical_keys": [[TEST_OBJ]],
    "size": [TEST_SIZE],
    "hash": {
        "value": [TEST_OBJ_HASH],
        "type": ["SHA256"],
    },
}
