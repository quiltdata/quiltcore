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
import quiltcore as qc
from upath import UPath

BKT="s3://quilt-example"
PKG="example/wellcharts"
dest="."
```

### Get Manifest

<!--pytest-codeblocks:cont-->
```python
reg = qc.CoreRegistry(UPath(BKT))
# versions = reg.namespace(PKG)
# manifest = versions.latest()
```

### Get Object

<!--pytest.mark.skip-->
```python
remote_object = manifest[-1]
print(remote_object.uri())
local = remote_object.put(dest)
```

### Verify Object

<!--pytest.mark.skip-->
```python
assert local_object.verify(remote_object.hash())
```
