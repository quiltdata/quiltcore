from tempfile import TemporaryDirectory

from pathlib import Path
from pytest import fixture
from upath import UPath

@fixture
def dir():
    with TemporaryDirectory() as tmpdirname:
        yield UPath(tmpdirname)


TEST_REG = "tests/example"
TEST_BKT = (Path.cwd() / TEST_REG).as_uri()
TEST_PKG = "manual/force"
TEST_TAG = "1680720965"
TEST_HASH = "3210f808ac0467726439191eea3bd0a66ab261122ee55758367620fedc77fe08"
TEST_SIZE = 30
# TEST_CAT = "https://open.quiltdata.com"

# TEST_URL = f"{TEST_CAT}/b/{TEST_BKT}/tree/.quilt/named_packages/{TEST_PKG}/{TEST_TAG}"
TEST_TABLE = f"{TEST_BKT}/.quilt/packages/{TEST_HASH}"
TEST_KEY = "ONLYME.md"
TEST_VER = "ihb.qioVby3gnRaMRFLNsxcX.Yir_K14"
TEST_OBJ = f"{TEST_BKT}/{TEST_PKG}/{TEST_KEY}?versionId={TEST_VER}"
TEST_OBJ_HASH = "df3e419dfd21f653651a5131e17bf41d82a9fd72baf2a93f634773353bd9d6c8"

TEST_ROW = {
    "logical_key": [TEST_KEY],
    "physical_keys": [[TEST_OBJ]],
    "size": [TEST_SIZE],
    "hash": {
        "value": [TEST_OBJ_HASH],
        "type": ["SHA256"],
    },
}
