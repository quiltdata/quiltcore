import logging
from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore

from .header import Header
from .udg.types import Dict3, Dict4, List4
from .udg.tabular import Tabular


class Table3(Tabular):
    """Abstract Pyarrow table of quilt3 JSON manifest."""

    #
    # Parse Table
    #

    def _get_table(self) -> pa.Table:
        with self.path.open(mode="rb") as fi:
            return pj.read_json(fi)

    def _get_head(self) -> pa.Table:
        """Extract header values into attributes."""
        return Header(self.path, first=self.first())

    def _get_body(self) -> pa.Table:
        """
        Extract header values into attributes.
        Return the Table without header row and columns
        """
        body = self.head.drop(self.table)
        return self.codec.decode_names(body)

    #
    # Query Table
    #

    def names(self) -> list[str]:
        if self.codec.name_col:
            return self.codec.name_col.to_pylist()
        return super().names()

    def get_dict3(self, key: str) -> Dict3:
        """Return the dict3 for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        index = self.codec.index_name(key).as_py()  # type: ignore
        if index < 0:
            raise ValueError(f"Key[{key}] not found in: {self.names()} ")
        pa_list = self.body.take([index]).to_pylist()
        pa_dict = pa_list[0]
        del pa_dict[self.codec.K_NAM]

        logging.debug(f"pa_dict: {pa_dict}")
        pa_dict3 = Dict3(**pa_dict)
        return pa_dict3

    def get_dict4(self, key: str) -> Dict4:
        """Return the dict4 for a child resource."""
        pa_dict3 = self.get_dict3(key)
        return self.codec.decode_dict3(pa_dict3)

    #
    # Translate Table
    #

    def relax(self, install_dir: Path, source_dir: Path | None = None) -> List4:
        list4 = super().relax(install_dir, source_dir)
        list4.insert(0, self.head.to_dict4())
        return list4
