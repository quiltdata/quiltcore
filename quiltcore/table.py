import logging
from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore
import pyarrow.json as pj  # type: ignore

from .header import Header
from .resource import Resource


class Table(Resource):
    """Abstract calls to pyarrow."""

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        with self.path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
        self.head = self._get_head()
        self.body = self._get_body()

    #
    # Parse Table
    #

    def _get_head(self) -> pa.Table:
        """
        Read the manifest into a pyarrow Table.
        Extract header values into attributes.
        Return the Table without header row and columns
        """
        first = self.table.take([0]).to_pydict()
        return Header(self.path, first=first)

    def _get_body(self) -> pa.Table:
        body = self.head.drop(self.table)
        return self._decode_table(body)

    def _decode_table(self, body: pa.Table) -> pa.Table:
        """
        URL-Decode appropriate columns of the manifest.
        """
        encoding = self.encodings()
        for old_col, new_col in encoding.items():
            self.decoded = True
            if old_col in body.column_names:
                body = body.append_column(
                    new_col,
                    self.decode_item(body.column(old_col)),
                )
        return body

    def decode_item(self, item):
        item_type = type(item)
        if isinstance(item, str):
            return self.decode(item)
        if isinstance(item, list):
            return [self.decode_item(item[0])]
        if isinstance(item, pa.ChunkedArray):
            return pa.chunked_array([self.decode_item(chunk) for chunk in item.chunks])
        if issubclass(item_type, pa.Array):
            return [self.decode_item(chunk) for chunk in item.to_pylist()]
        raise TypeError(f"Unexpected type: {item_type}")


    def filter(self, col: str, key: str) -> dict:
        """Return the dict for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        rows = self.body.filter(pc.field(col) == key)
        if rows.num_rows == 0:
            raise KeyError(f"Key [{key}] not found in {col} of {self.path}")
        row = rows.to_pydict()
        return row
   
