#!/usr/bin/env python
import os
from quiltcore import Domain, UDI
from tempfile import TemporaryDirectory
from upath import UPath

TEST_BKT = "s3://quilt-example"
TEST_PKG = "akarve/amazon-reviews"
TEST_TAG = "1570503102"
TEST_HASH = "ffe323137d0a84a9d1d6f200cecd616f434e121b3f53a8891a5c8d70f82244c2"
TEST_KEY = "camera-reviews"
WRITE_BKT = os.environ.get("WRITE_BUCKET")
SOURCE_URI = f"quilt+{TEST_BKT}#package={TEST_PKG}:{TEST_TAG}"
DEST_URI = f"quilt+{TEST_BKT}#package={TEST_PKG}:{TEST_TAG}"

remote = UDI.FromUri(SOURCE_URI)
print(f"remote: {remote}")
with TemporaryDirectory() as tmpdir:
    local = UPath(tmpdir)
    domain = Domain.FromLocalPath(local)
    print(f"domain: {domain}")
    folder = domain.pull(remote)
    print(f"folder: {folder}")
    if WRITE_BKT:
        tag = domain.push(folder, remote=UDI.FromUri(DEST_URI))
        print(f"tag: {tag}")
