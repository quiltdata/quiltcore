import logging  # noqa: F401
from pathlib import Path

import pyarrow as pa  # type: ignore

from .udg.types import Dict4
from .udg.tabular import Tabular


class Table4(Tabular):
    """Abstract away calls to, and encoding of, pyarrow."""

    def __init__(self, parquet_path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(parquet_path, **kwargs)
        self.table = self.Read4(self.path)
        self.head = Dict4(**self.first(self.table))
        self.body = self.table.slice(1)

    #
    # Query Table
    #

    def names(self) -> list[str]:
        return self.body.column("name").to_pylist()

    def get_dict4(self, key: str) -> Dict4:
        """Return the dict4 for a child resource."""
        row = self.body.filter([pa.field("name", pa.string()) == key])
        return Dict4(**row.to_pydict())
