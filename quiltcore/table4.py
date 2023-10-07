import logging  # noqa: F401
from pathlib import Path

import pyarrow as pa  # type: ignore

# import parquet from pyarrow
from pyarrow.parquet import ParquetFile  # type: ignore

from .resource import Resource
from .udg.codec import Dict4, List4
from .udg.tabular import Tabular


class Table4(Tabular):
    """Abstract away calls to, and encoding of, pyarrow."""

    def __init__(self, parquet_path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(parquet_path, **kwargs)
        with self.path.open(mode="rb") as fi:
            self.table = ParquetFile(fi).read()
        self.head = Dict4(**self.first(self.table))
        self.body = self.table.slice(1)

    #
    # Query Table
    #

    def names(self) -> list[str]:
        return self.body.column("name").to_pylist()

    def get_dict4(self, key: str) -> Dict4:
        """Return the dict4 for a child resource."""
        row = self.body.filter(pa.field("name") == key)
        return Dict4(**row.to_pydict())

    #
    # Translate Table
    #

    def relax(self, dest_dir: Path) -> List4:
        dict4s = [self.head]
        for name, row in self.items():
            new_dest = dest_dir / name
            path = Resource.AsPath(row.place)
            with path.open("rb") as fi:
                new_dest.write_bytes(fi.read())
            row.place = self.codec.AsStr(new_dest)
            dict4s.append(row)
        return dict4s
