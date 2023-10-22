import logging

from os import environ
from pathlib import Path

from quiltcore import Types, UDI

root = logging.getLogger()
root.setLevel(logging.INFO)  # DEBUG

LOCAL_ONLY = environ.get("LOCAL_ONLY") or False

TEST_BKT = "s3://udp-spec"
LOCAL_VOL = "tests/example"
TEST_PATH = Path.cwd() / LOCAL_VOL
TEST_VOL = Types.AsString(TEST_PATH)
LOCAL_URI = "file://" + TEST_VOL


TEST_PKG = "manual/force"
TEST_TAG = "1689722104"
TEST_HASH = "5f1b1e4928dbb5d700cfd37ed5f5180134d1ad93a0a700f17e43275654c262f4"
TEST_SIZE = 30
TEST_KEY = "ONLYME.md"
TEST_VER = "VetrR_Vukeiiv.NkXZXpQFKEibsK0QW3"
TEST_OBJ = f"{TEST_VOL}/{TEST_PKG}/{TEST_KEY}?versionId={TEST_VER}"
TEST_OBJ_HASH = "df3e419dfd21f653651a5131e17bf41d82a9fd72baf2a93f634773353bd9d6c8"

TEST_MAN = f"{TEST_VOL}/.quilt/packages/{TEST_HASH}"
TEST_PARQUET = f"{TEST_VOL}/.quilt/packages/12201234.parquet"
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

LOCAL_UDI = f"quilt+{LOCAL_URI}#{UDI.K_PKG}={TEST_PKG}"


def not_win():
    return not Types.OnWindows()


T_BKT = "quilt-example"
T_PKG = "examples/wellplates"
FIRST_PKG = "akarve/amazon-reviews"

CATALOG_URL = f"https://open.quiltdata.com/b/{T_BKT}/packages/{T_PKG}"
TEST_URI = (
    f"quilt+s3://{T_BKT}#package={T_PKG}"
    + "@e1f83ce3dc7b9487e5732d58effabad64065d2e7401996fa5afccd0ceb92645c"
    + "&path=README.md&catalog=open.quiltdata.com"
)
BKT_URI = f"quilt+s3://{T_BKT}"
PKG_URI = f"quilt+s3://{T_BKT}#{UDI.K_PKG}={T_PKG}@e1f83ce3dc7b"
PKG2_URI = f"quilt+s3://{T_BKT}#{UDI.K_PKG}=examples/echarts:latest"
PTH_URI = f"quilt+s3://{T_BKT}#{UDI.K_PKG}={T_PKG}&{UDI.K_PTH}=README.md"
VER_URI = f"quilt+s3://{T_BKT}#{UDI.K_PKG}={T_PKG}"
PRP_URI = f"{VER_URI}&{UDI.K_PTH}=README.md&{UDI.K_PRP}=*"

TEST_URIS = [TEST_URI, BKT_URI, PKG_URI, PKG2_URI, PTH_URI, PRP_URI, VER_URI]
