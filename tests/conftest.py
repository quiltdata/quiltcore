from os import environ
from pathlib import Path
from sys import platform
from quiltcore import Changes

LOCAL_ONLY = environ.get("LOCAL_ONLY") or False

TEST_BKT = "s3://udp-spec"
LOCAL_VOL = "tests/example"

TEST_VOL = str(Path.cwd() / LOCAL_VOL)
TEST_PKG = "manual/force"
TEST_TAG = "1689722104"
TEST_HASH = "5f1b1e4928dbb5d700cfd37ed5f5180134d1ad93a0a700f17e43275654c262f4"
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


def not_win():
    return not platform.startswith("win")

class MockChanges(Changes):
    FILENAME = "filename.txt"
    FILETEXT = "hello world"

    def __init__(self, dir: Path, **kwargs):
        super().__init__(dir, **kwargs)
        self.infile = (dir / self.FILENAME).resolve()
        self.infile.write_text(self.FILETEXT)
        self.post(self.infile)

