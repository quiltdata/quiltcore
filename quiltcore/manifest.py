from pathlib import Path

import logging
import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore
import pyarrow.json as pj  # type: ignore
from typing_extensions import Self
from upath import UPath

from .resource import Resource


class Manifest(Resource):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Blob with Path to the Place data actually lives
    """

    # TODO: cache Blobs to avoid repeated lookups

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        try:
            self.body = self.setup_table(path)
        except FileNotFoundError:
            logging.warning(f"Manifest not found: {path}")
        self.name_col = self.cf.get_str("schema/name", "logical_key")
        self.place_col = self.cf.get_str("schema/place", "physical_keys")

    def setup_table(self, path: Path) -> pa.Table:
        with path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
        first = self.table.take([0]).to_pydict()
        headers = self.cf.get_dict("schema/headers")
        keys = list(headers.keys())
        for key in keys:
            setattr(self, key, first[key][0])
        return self.table.drop_columns(keys).slice(1)

    #
    # Private Methods for child resources
    #

    def child_row(self, key: str) -> dict:
        """Return the dict for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        rows = self.body.filter(pc.field(self.name_col) == key)
        if rows.num_rows == 0:
            raise KeyError(f"Key [{key}] not found in {self.name_col} of {self.path}")
        return rows.to_pydict()

    def child_path(self, key: str) -> Path:
        """Return the Path for a child resource."""
        row = self.child_row(key)
        place = row[self.place_col][0][0]
        return UPath(place)

    def child_args(self, key: str) -> dict:
        """Return the parameters for a child resource."""
        row = self.child_row(key)
        return {"row": row, "parent": self}

    #
    # Public HTTP-like Methods
    #

    def list(self) -> list[Resource]:
        """List all child resources."""
        names = self.body.column(self.name_col).to_pylist()
        return [self.child(self.child_path(x), x) for x in names]
