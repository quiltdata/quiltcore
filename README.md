# QuiltCore

QuiltCore is a library for building and running [Quilt](https://quiltdata.com) data packages.
It is designed to leverage standard open source technology and YAML configuration files
so that it can easily be ported to other languages and platforms.

This initial implementation is in Python.

## Key Technologies

- Apache [Arrow](https://arrow.apache.org/) for reading, writing, and representing manifests
  - [PyArrow](https://arrow.apache.org/docs/python/) for Python bindings to Arrow
- fsspec [filesystems](https://filesystem-spec.readthedocs.io/en/latest/)
  for reading and writing files from various sources
- [PyYAML](https://pyyaml.org/) for reading and writing YAML configuration files

## Example

```bash
poetry install
```

```python
from quiltcore import Registry
from tempfile import TemporaryDirectory
from upath import UPath

TEST_BKT = "s3://quilt-example"
TEST_PKG = "akarve/amazon-reviews"
TEST_TAG = "1570503102"
TEST_HASH = "ffe323137d0a84a9d1d6f200cecd616f434e121b3f53a8891a5c8d70f82244c2"
TEST_KEY = "camera-reviews"
```

### Get Manifest

<!--pytest-codeblocks:cont-->
```python
path = UPath(TEST_BKT)
registry = Registry(path)
named_package = registry.get(TEST_PKG)
manifest = named_package.get(TEST_TAG)
entry = manifest.get(TEST_KEY)
```

### Get Object

<!--pytest-codeblocks:cont-->
```python
with TemporaryDirectory() as tmpdir:
  dest = UPath(tmpdir)
  outfile = dest / TEST_KEY
  entry.get(tmpdir)
  print(outfile.resolve())
  assert outfile.exists()
  local_bytes = outfile.read_bytes()
  assert entry.verify(local_bytes)
```
