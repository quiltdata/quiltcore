import logging

from jsonlines import Writer  # type: ignore
from pathlib import Path
from re import compile
from typing import Iterator
from urllib.parse import parse_qs, urlparse

from .domain import Domain
from .entry import Entry
from .header import Header
from .table import Table
from .udg.codec import Dict3, asdict
from .udg.child import Child


class Manifest2(Child):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    IS_LOCAL = compile(r"file:\/*")
    IS_REL = "./"
    IS_URI = ":/"

    @classmethod
    def GetQuery(cls, uri: str, key: str) -> str:
        """Extract key from URI query string."""
        query = urlparse(uri).query
        if not query:
            return ""
        qs = parse_qs(query)
        vlist = qs.get(key)
        return vlist[0] if vlist else ""

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

    #
    # Private Methods for child resources
    #

    def __iter__(self) -> Iterator[str]:
        """List all row names."""
        return (name for name in self.table().names())

    def find_store(self, next=None) -> Path:
        """Return the datastore path."""
        next = next or self
        parent = self.parent
        if parent is None:
            raise ValueError("No parent for {self}")
        if isinstance(parent, Domain):
            return parent.store
        return self.find_store(parent)

    def _child_place(self, place: str) -> str:
        if self.IS_REL not in place:
            return place
        if self.IS_LOCAL.match(place) is not None:
            place = self.IS_LOCAL.sub("", place)
        path = self.find_store() / place
        logging.debug(f"{place} -> {path} [{path.absolute()}]")
        return str(path)

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        row = self.table().get_dict4(key)
        place = row.place
        drow = asdict(row)
        drow[self.cf.K_PLC] = self._child_place(place)
        v = self.GetQuery(place, self.cf.K_VER)
        if len(v) > 0:
            drow[self.cf.K_VER] = v
        return drow
