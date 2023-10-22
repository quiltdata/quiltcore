import logging  # noqa: F401

import pyarrow as pa  # type: ignore

from .udg.types import Dict4
from .udg.tabular import Tabular


class Table4(Tabular):
    """Abstract Pyarrow table of quilt4 Parquet manifest."""

    def _get_table(self) -> pa.Table:
        return self.ReadParquet(self.path)

    def _get_head(self) -> pa.Table:
        """Extract header values into attributes."""
        return Dict4(**self.first())

    def _get_body(self) -> pa.Table:
        """
        Extract header values into attributes.
        Return the Table without header row and columns
        """
        return self.table.slice(1)

    #
    # Query Table
    #

    def names(self) -> list[str]:
        return self.table.column("name").to_pylist()

    def get_row(self, key: str) -> dict:
        """Return the row for a child resource."""
        condition = pa.compute.equal(self.table.column("name"), key)
        result = self.table.filter(condition).to_pylist()
        return result[0] if len(result) == 1 else {}

    def get_dict4(self, key: str) -> Dict4:
        """Return the dict4 for a child resource."""
        row = self.get_row(key)
        assert row, f"Missing row for {key}"
        return Dict4(**row)
