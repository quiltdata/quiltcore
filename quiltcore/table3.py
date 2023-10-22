import logging

import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore

from .udg.header import Header
from .udg.types import Dict3, Dict4
from .udg.tabular import Tabular


class Table3(Tabular):
    """Abstract Pyarrow table of quilt3 JSON manifest."""

    #
    # Parse Table
    #

    def _get_table(self) -> pa.Table:
        with self.path.open(mode="rb") as fi:
            return pj.read_json(fi)

    def _get_head(self) -> Dict4:
        """Extract header values into Dict4 attributes."""
        self.header = Header(self.first())
        return self.header.to_dict4()

    def _get_body(self) -> pa.Table:
        """
        Extract header values into attributes.
        Return the Table without header row and columns
        """
        assert self.header, f"Header not found for {self.path}:\n${self.table}"
        body = self.header.drop(self.table)
        return self.codec.decode_names(body)

    #
    # Query Table
    #

    def names(self) -> list[str]:
        if self.codec.name_col:
            return [self.HEADER_NAME] + self.codec.name_col.to_pylist()
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
        if key == self.HEADER_NAME:
            return self.head
        pa_dict3 = self.get_dict3(key)
        return self.codec.decode_dict3(pa_dict3)
