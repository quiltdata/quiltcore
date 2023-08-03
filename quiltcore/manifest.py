import logging
from pathlib import Path

from jsonlines import Writer  # type: ignore

from .entry import Entry
from .header import Header
from .resource_key import ResourceKey
from .table import Table
from .yaml.codec import Dict3, asdict


class Manifest(ResourceKey):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

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

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self._table: Table | None = None

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

    def hash_quilt3(self) -> str:
        """Legacy quilt3 hash of the contents."""
        return self.name

    #
    # Private Methods for child resources
    #

    def _child_names(self, **kwargs) -> list[str]:
        """List all child resource names."""
        return self.table().names()

    def _child_place(self, place: str) -> str:
        if self.IS_REL not in place:
            return place
        if self.IS_LOCAL.match(place) is not None:
            place = self.IS_LOCAL.sub("", place)
        if self.ARG_REG not in self.args:
            raise KeyError(f"No registry root available in {self.args.keys()}")
        reg = self.args[self.ARG_REG]
        path = reg.root / place
        logging.debug(f"{place} -> {path} [{path.absolute()}]")
        return str(path)

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        row = self.table().get_dict4(key)
        place = row.place
        drow = asdict(row)
        drow[self.codec.K_PLC] = self._child_place(place)
        v = self.GetVersion(place)
        if len(v) > 0:
            drow[self.KEY_VER] = v
        return drow
