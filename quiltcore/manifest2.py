import logging

from jsonlines import Writer  # type: ignore
from pathlib import Path
from re import compile
from typing import Iterator

from .entry import Entry
from .header import Header
from .table import Table
from .udg.codec import Dict3, Multihash, asdict
from .udg.child import Child


class Manifest2(Child):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    IS_LOCAL = compile(r"file:\/*")
    IS_REL = "./"
    IS_URI = ":/"

    @staticmethod
    def WriteToPath(head: Header, entries: list[Entry], path: Path) -> None:
        """Write manifest contents to _path_"""
        logging.debug(f"WriteToPath: {path}")
        rows = [entry.to_dict3() for entry in entries]  # type: ignore
        with path.open(mode="wb") as fo:
            with Writer(fo) as writer:
                head_dict = head.to_dict()
                print(f"head_dict: {head_dict}")
                writer.write(head_dict)
                for row in rows:
                    if not isinstance(row, Dict3):
                        raise ValueError("")
                    writer.write(asdict(row))

    def __init__(self, name: str, parent: Child, **kwargs):
        super().__init__(name, parent, **kwargs)
        self._table: Table | None = None

    def extend_parent_path(self, key: str) -> Path:
        if hasattr(self.parent, "manifests"):
            base = getattr(self.parent, "manifests")
            assert isinstance(base, Path)
            assert base.exists()
            return base / key
        raise ValueError(f"Parent has no manifests: {self.parent}")
    #
    # Initialize Table
    #

    def table(self) -> Table:
        if not hasattr(self, "_table") or self._table is None:
            try:
                self._table = Table(self.path, **self.args)
            except FileNotFoundError:
                logging.warning(f"Manifest not found: {self.path}")
        if not isinstance(self._table, Table):
            raise TypeError(f"Expected Table, got {type(self._table)}")
        return self._table

    def head(self):
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
