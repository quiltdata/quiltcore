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

Streamlined manifest schema ("Dict4")

- name
- place / path
- size
- multihash : quilt3_hash : struct_hash
- info / sys_meta
- meta / user_meta

### Principles

- Must correctly read and write legacy schema
- Present only new schema
- decode dict into Dict4
- encode attrs into UDI (Universal Data Identifier)

## Architecture

### 1. Cross-Platform Open Source

- Arrow for reading/writing manifests
- URI-based filesystem abstractions  (fsspec, nio, etc.)
- Multihash for creating/verifying content hashes

### 2. quiltcore.yaml

Rather than hard-coding any constants, all configuration
parameters are stored in a [yaml file](../quiltcore/config/quiltcore.yaml).

By making explicit what was previously implicit, this should:

1. Simplify porting to other languages (i.e., Java),
   by making it easy for either humans or code to reading

2. Force concrete discussion about naming conventions
   and other design decisions

3. Rationalize mechanisms for defining alternate manifest formats

### 2. Universal Data Graph

Effectively everything is a [Node](../quiltcore/udg/node.py)
in the Universal Data Graph (UDG):

- Domains (storage + mappings)
- Namespaces (package identifiers)
- Manifests (package mappings)
- Entries (package contents)
- Builder (package construction)

Nodes inherit:

- Core types (e.g., Dict4)
- Keyed (implements the Python `MutableMapping` interface)
- Verifiable (for computing/verifying hashes)

Node contains a `Codec` for converting to/from the old quilt3 schema.

Codec inhertis from the `Config` class that uses `quiltcore.yaml` file.
This implementation dynamically generates behavior directly
from the configuration file into single-purpose sublasses.
Other implementations may choose to generate code statically.

### 3. Entry

The final leaf node is the [Entry](../quiltcore/entry.py) class.
This tracks information for each manifest entry, including:

- name: str (logical_key)
- place: str (physical_key)
- size: int
- multihash: str[hex]
- info: object[metadata]
- meta: object[metadata]

This also handles individually verifying and uploading data.

## Open Issues

- Workflow Support

- Handling S3 Version IDs

- Aggregate uploads/downloads (Async)

- Testing Python Pathlib on Minio, Azure, etc.
