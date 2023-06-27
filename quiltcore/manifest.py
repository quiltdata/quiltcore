from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore

class CoreManifest:
    """In-memory representation of a serialized package manifest."""

    @staticmethod
    def FromPath(path: Path):
        """Create a manifest from a file path."""
        with path.open(mode='rb') as fi:
            table = pj.read_json(fi)
            return CoreManifest(table)


    def __init__(self, table: pa.Table):
        self.table = table
