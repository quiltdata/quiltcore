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
- Entry

These make use of the 'Config' class which loads and
manages the 'quiltcore.yaml' configuration file.

"""

from .builder import Builder  # noqa: F401
from .builder2 import FolderBuilder  # noqa: F401
from .changes import Changes  # noqa: F401
from .delta import Delta  # noqa: F401
from .domain import Domain  # noqa: F401
from .entry import Entry  # noqa: F401
from .entry2 import Entry2  # noqa: F401
from .factory import Factory, quilt  # noqa: F401
from .header import Header  # noqa: F401
from .manifest import Manifest  # noqa: F401
from .manifest2 import Manifest2  # noqa: F401
from .namespace import Namespace  # noqa: F401
from .namespace2 import Namespace2  # noqa: F401
from .registry import Registry  # noqa: F401
from .resource import Resource  # noqa: F401
from .scheme import Scheme  # noqa: F401
from .table3 import Table3  # noqa: F401
from .table4 import Table4  # noqa: F401
from .udg.types import Dict3, Dict4, Hash3, Multihash, Types  # noqa: F401
from .udg.codec import Codec  # noqa: F401
from .udg.folder import Folder  # noqa: F401
from .udg.keyed import Keyed  # noqa: F401
from .udg.node import Node  # noqa: F401
from .udg.verifiable import Verifiable  # noqa: F401
from .volume import Volume  # noqa: F401
from .config.config import Config  # noqa: F401
from .config.data import Data  # noqa: F401
from .config.spec import Spec  # noqa: F401
from .config.udi import UDI  # noqa: F401
