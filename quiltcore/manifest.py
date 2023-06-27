from pathlib import Path
from typing_extensions import Self

import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore

from .resource import CoreResource

class CoreManifest(CoreResource):
    """In-memory representation of a serialized package manifest."""

    def __init__(self, path: Path, parent: CoreResource|None = None):
        super().__init__(path, parent)
        with path.open(mode='rb') as fi:
            self.table = pj.read_json(fi)
