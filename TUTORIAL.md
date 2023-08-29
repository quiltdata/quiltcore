# Tutorial: Quilt's Magic UAND

Quilt is a lightweight data abstraction layer that provides Uniform Affordances for Nonuniform Data ("UAND"). It unites diverse decentralized domains into a Universal Data Graph ("UDG") via a hierarchical logical namespace. 

In Python it looks like this (though convenience APIs can use URIs or defaults instead):

```python
from quiltcore import quilt

dataset = quilt["file"]["./example"]["test/package"]["latest"]
assert "Hello world" == dataset["README.md"].read_text()
assert "Ernie" == dataset.meta["Author"]["First"]
assert 123 == dataset["data.parquet"]["count"][0]
```

Every Node in the UDG has a `name`, `type` and (except for the root) a `parent`.
Nodes are also Verifiable -- meaning they support the methods `hash` and `verify`:

```python

Multihash = str

def hash(self) -> Multihash: pass

def digest(self, contents: bytes) -> Multihash: pass

def verify(self, contents: bytes) -> bool: pass
```

The different Node types are:

1. Scheme (eg, s3 or file)
2. Domain (eg, bucket or folder)
3. Namespace (prefix/suffix)
4. Manifest (by named tag or numerical timestamp)
5. Metadata
6. Entry

The first five are known as Registries, and are always "KeyedObjects" (internal nodes) that allow path traversal.
Only certain Entry types (e.g., structured data files) are KeyedObjects.
Note that Metadata and Entry will have children that are not Nodes, but may be KeyedObjects.





```python

```

```python

```


