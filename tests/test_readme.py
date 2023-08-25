from quiltcore import Registry
from tempfile import TemporaryDirectory
from upath import UPath
from pytest import mark

TEST_BKT = "s3://quilt-example"
TEST_PKG = "akarve/amazon-reviews"
TEST_TAG = "1570503102"
TEST_HASH = "ffe323137d0a84a9d1d6f200cecd616f434e121b3f53a8891a5c8d70f82244c2"
TEST_KEY = "camera-reviews"

@mark.skip(reason="Duplicates README codeblock (and is slow)")
def test_readme():
    path = UPath(TEST_BKT)
    registry = Registry(path)
    named_package = registry.get(TEST_PKG)
    manifest = named_package.get(TEST_TAG)
    entry = manifest.get(TEST_KEY)
    with TemporaryDirectory() as tmpdir:
        dest = UPath(tmpdir)
        outfile = dest / TEST_KEY
        entry.get(tmpdir)
        print(outfile.resolve())
        assert outfile.exists()
        local_bytes = outfile.read_bytes()
        assert entry.verify(local_bytes)
