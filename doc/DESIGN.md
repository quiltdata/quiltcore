# QuiltCore Design

## Objectives

This initial Python implementation of QuiltCore
attempts to define a next-generation architecture and primitives
("plumbing")for reading and writing Quilt packages that make it easy to:

1. Implement in other languages
2. Extend to other storage backends (blobs, filesystems, relational?)
3. Support alternate manifest serializations (and additional semantics)
4. Wrap in application-specific "porcelain" (convenience APIs)

## Schema

Streamlined manifest schema:

- name
- place / path
- size
- multihash : quilt3_hash : struct_hash
- meta / user_meta

### Principles

- Must correctly read and write legacy schema
- Present only new schema
- decode dict into dict
- encode attrs into dict

## Architecture

### 1. Cross-Platform Open Source

- Arrow for reading/writing manifests
- URI-based filesystem abstractions  (fsspec, nio, etc.)
- Multihash for creating/verifying content hashes

### 2. quiltcore.yaml

Rather than hard-coding any constants, all configuration
parameters are stored in a [yaml file](../quiltcore/yaml/quiltcore.yaml).

By making explicit what was previously implicit, this should:

1. Simplify porting to other languages (i.e., Java),
   by making it easy for either humans or code to reading

2. Force concrete discussion about naming conventions
   and other design decisions

3. Rationalize mechanisms for defining alternate manifest formats

### 2. esource

The [esource](../quiltcore/resource.py) base class
provides a common set of abstractions for:

1. Accessing configuration parameters

2. Creating child resources

3. Supporting various HTTP-like verbs (e.g., GET, PUT, POST, DELETE, VERIFY)

This implementation dynamically generates behavior directly
from the configuration file into single-purpose sublasses.
Other implementations may choose to generate code statically.

### 3. Entry

The final leaf node is the [Entry](../quiltcore/entry.py) class.
This tracks information for each manifest entry, including:

- name: str (logical_key)
- path: Path (physical_key)
- size: int
- hash: str[hex]
- multihash: str[hex]
- meta: object[metadata]

This also handles individually verifying and uploading data.

## Open Issues

- Class naming conventions

- Formal specification for conformance

- Aggregate uploads/downloads (Async)

- Schema versioning (proactive? where/how?)
