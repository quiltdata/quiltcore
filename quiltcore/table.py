import logging
from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore

from .header import Header
from .resource_key import ResourceKey
from .yaml.codec import Codec, Dict3, Dict4


class Table(ResourceKey):
    """Abstract away calls to, and encoding of, pyarrow."""

    def __init__(self, path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(path, **kwargs)
        self.codec = Codec()
        with self.path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
        self.head = self._get_head()
        self.body = self._get_body()

    #
    # Parse Table
    #

    def _get_head(self) -> pa.Table:
        """Extract header values into attributes."""
        first = self.table.take([0]).to_pylist()[0]
        return Header(self.path, first=first)

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
        return []

    def get_dict4(self, key: str) -> Dict4:
        """Return the dict for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        index = self.codec.index_name(key).as_py()  # type: ignore
        if index < 0:
            raise ValueError(f"Key[{key}] not found in: {self.names()} ")
        pa_list = self.body.take([index]).to_pylist()
        pa_dict = pa_list[0]
        del pa_dict[self.codec.K_NAM]

        logging.debug(f"pa_dict: {pa_dict}")
        pa_dict3 = Dict3(**pa_dict)
        return self.codec.decode_dict(pa_dict3)
