"""

This Python package is the very first implementation of QuiltCore,
a next-generation architecture and primitives ("plumbing")
for reading and writing Quilt packages:

QuiltCore is makes Quilt easy to:

1. Implement in other languages
2. Extend to other storage backends (blobs, filesystems, etc.)
3. Support alternate manifest serializations (and additional semantics)
4. Wrap in application-specific "porcelain" (convenience APIs)

The core Resource classes are, in order of increasing specialization:

- Resource
- Registry
- Namespace
- Manifest
- Blob

These make use of the 'Config' class which loads and
manages the 'quiltcore.yaml' configuration file.

"""

from .blob import Blob  # noqa: F401
from .yaml.config import Config  # noqa: F401
from .manifest import Manifest  # noqa: F401
from .namespace import Namespace  # noqa: F401
from .registry import Registry  # noqa: F401
from .resource import Resource  # noqa: F401
