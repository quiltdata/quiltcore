import logging
from pathlib import Path
from typing import Iterator

from .table3 import Table3, Tabular
from .table4 import Table4
from .udg.child import Child, Node
from .udg.types import Multihash


class Manifest2(Child):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    def __init__(self, name: str, parent: Node, **kwargs):
        super().__init__(name, parent, **kwargs)
        self._table: Tabular | None = None

    def extend_parent_path(self, key: str) -> Path:
        if hasattr(self.parent, "manifests"):
            base = getattr(self.parent, "manifests")
            assert isinstance(base, Path)
            assert base.exists()
            path = Tabular.FindTablePath(base / key)
            assert path.exists(), f"Manifest not found: {path}"
            return path
        raise ValueError(f"Parent has no manifests: {self.parent}")

    def relax(self, install_dir: Path, manifests: Path, parent: Node) -> "Manifest2":
        """
        1. Relax table relative to Store into Dest
        2. Calculate Mpath for storing Manifest
        3. Write relaxed table to Mpath
        4. Return new Manifest inside that Namespace
        """
        list4 = self.table().relax(install_dir)
        Tabular.Write4(list4, manifests / self.name)
        # Requires `parent` to be the Namespace containing `manifests`
        return Manifest2(self.name, parent)

    #
    # Initialize Table
    #

    def table(self) -> Tabular:
        """Load from Parquet or JSON."""
        if not hasattr(self, "_table") or self._table is None:
            try:
                factory = Table4 if self.path.suffix == Tabular.EXT4 else Table3
                self._table = factory(self.path, **self.args)
            except FileNotFoundError:
                logging.warning(f"Manifest not found: {self.path}")
        if not isinstance(self._table, Tabular):
            raise TypeError(f"Expected Table, got {type(self._table)}")
        return self._table

    def header(self):
        return self.table().head

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
