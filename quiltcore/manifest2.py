import logging
from pathlib import Path
from typing import Iterator

from .table3 import Table3
from .udg.child import Child
from .udg.codec import List4, Multihash
from .udg.tabular import Tabular


class Manifest2(Child):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    def __init__(self, name: str, parent: Child, **kwargs):
        super().__init__(name, parent, **kwargs)
        self._table: Tabular | None = None

    def extend_parent_path(self, key: str) -> Path:
        if hasattr(self.parent, "manifests"):
            base = getattr(self.parent, "manifests")
            assert isinstance(base, Path)
            assert base.exists()
            return base / key
        raise ValueError(f"Parent has no manifests: {self.parent}")

    def relax(self, dest: Path) -> List4:
        """
        1. Relax table to new dest column
        2. Write to Parquet file
        """
        dict4s = self.table().relax(dest)
        logging.debug(f"dict4s: {dict4s}")
        return dict4s

    #
    # Initialize Table
    #

    def table(self) -> Tabular:
        if not hasattr(self, "_table") or self._table is None:
            try:
                self._table = Table3(self.path, **self.args)
            except FileNotFoundError:
                logging.warning(f"Manifest not found: {self.path}")
        if not isinstance(self._table, Tabular):
            raise TypeError(f"Expected Table, got {type(self._table)}")
        return self._table

    def head(self):
        table = self.table()
        if isinstance(table, Table3):
            return table.head
        raise TypeError(f"Expected Table3, got {type(self.table())}")

    #
    # Hash functions
    #

    def q3hash(self) -> str:
        """Legacy quilt3 hash of the contents."""
        return self.name

    def _multihash_contents(self) -> Multihash:
        return self.cf.decode_q3hash(self.q3hash())

    #
    # Private Methods for child resources
    #

    def __iter__(self) -> Iterator[str]:
        """List all row names."""
        return (name for name in self.table().names())
