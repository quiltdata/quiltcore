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

```python
import quiltcore as qc

BKT="s3://quilt-example"
PKG="example/wellcharts"
dest="."

# Get Manifest

reg = qc.CoreRegistry(BKT)
versions = reg.namespace(PKG)
manifest = versions.latest()

# Get Object

remote_object = manifest[-1]
print(remote_object.uri())
local = remote_object.put(dest)

# Verify Object

assert local_object.verify(remote_object.hash())
```
