# Tutorial: Quilt's Magic UAND

Quilt is a lightweight data abstraction layer that provides Uniform Affordances for Nonuniform Data ("UAND").
It unites diverse decentralized domains into a Universal Data Graph ("UDG") via a hierarchical logical namespace.
In Python it looks like this (though convenience APIs can use URIs or defaults instead):

## Example

```python
from quiltcore import quilt, Domain, Manifest, Entry

dataset = quilt["file"]["./tests/example"]["manual/force"]["latest"]
assert isinstance(dataset, Manifest)
```

## UDG Node Types

The main Node types, in order, are:

0. Factory (root object, i.e. `quilt`)
1. Scheme (eg, 's3' or 'file')
2. Domain (eg, _bucket_ or _folder_)
3. Namespace (_prefix/suffix_)
4. Manifest (by named _tag_ or numerical _timestamp_)
5. Metadata (JSON)
6. Entry (name, place, size, hash)

The first five are known as Registries, and are always "KeyedObjects" (internal nodes) that allow path traversal.
Only certain Entry types (e.g., structured data files) are valid KeyedObjects.
Note that Metadata and Entry will have children that are not Nodes, but may be KeyedObjects.

The Manifest is the heart of the UDG, and maps logical _names_ to physical _places_.

<!--pytest.mark.skip-->
```python
assert "Hello world" == dataset["README.md"].read_text()
assert "Ernie" == dataset.meta["Author"]["First"]
assert 123 == dataset["data.parquet"]["count"][0]
```
<!--pytest-codeblocks:cont-->

Every Node in the UDG has a `name`, `type` and (except for the root) a `parent`.
Nodes are also Verifiable -- meaning they support the methods `hash` and `verify`:

```python

Multihash = str

def hash(self) -> Multihash: pass

def digest_bytes(self, contents: bytes) -> Multihash: pass

def verify(self, contents: bytes) -> bool: pass
```

## Adding Nodes

```python

```

```python

```
