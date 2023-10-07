import logging
from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore

from .header import Header
from .udg.codec import Dict3, Dict4, List4
from .udg.tabular import Tabular


class Table3(Tabular):
    """Abstract away calls to, and encoding of, pyarrow."""

    def __init__(self, json_path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(json_path, **kwargs)
        with self.path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
        self.head = self._get_head()
        self.body = self._get_body()

    #
    # Parse Table
    #

    def _get_head(self) -> pa.Table:
        """Extract header values into attributes."""
        return Header(self.path, first=self.first(self.table))

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
        return self.codec.decode_dict(pa_dict3)

    #
    # Translate Table
    #

    def relax(self, dest_dir: Path) -> List4:
        list4 = super().relax(dest_dir)
        list4.insert(0, self.head.to_dict4())
        return list4
