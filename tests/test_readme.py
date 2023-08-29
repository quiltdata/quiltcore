from quiltcore import Registry, Entry
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
    named_package = registry.getResource(TEST_PKG)
    manifest = named_package.getResource(TEST_TAG)
    entry = manifest.getResource(TEST_KEY)
    if not isinstance(entry, Entry):
        raise TypeError(f"Expected Entry, got {type(entry)}")
    with TemporaryDirectory() as tmpdir:
        dest = UPath(tmpdir)
        outfile = dest / TEST_KEY
        entry.install(tmpdir)
        print(outfile.resolve())
        assert outfile.exists()
        local_bytes = outfile.read_bytes()
        assert entry.verify(local_bytes)
