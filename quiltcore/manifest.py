from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore
import pyarrow.json as pj  # type: ignore
from typing_extensions import Self
from upath import UPath

from .resource import CoreResource


class CoreManifest(CoreResource):
    """In-memory representation of a serialized package manifest."""

    # TODO: cache Blobs to avoid repeated lookups
    # TODO: improve/replace child(key) handling

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        with path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
        self.body = self.setup()
        self.name_col = self.cf.get_str("schema/name", "logical_key")
        self.loc_col = self.cf.get_str("schema/location", "physical_keys")

    def setup(self) -> pa.Table:
        first = self.table.take([0]).to_pydict()
        headers = self.cf.get_dict("schema/headers")
        keys = list(headers.keys())
        for key in keys:
            setattr(self, key, first[key][0])
        return self.table.drop_columns(keys).slice(1)

    def child_row(self, key: str) -> dict:
        """Return the dict for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        rows = self.body.filter(pc.field(self.name_col) == key)
        if rows.num_rows == 0:
            raise KeyError(f"Key [{key}] not found in {self.name_col} of {self.path}")
        return rows.to_pydict()

    def child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        row = self.child_row(key)
        loc = row[self.loc_col][0][0]
        return UPath(loc)

    def child_args(self, key: str) -> dict:
        """Return the parameters for a child resource."""
        row = self.child_row(key)
        return {"row": row, "parent": self}

    def list(self) -> list[Self]:
        """List all child resources."""
        names = self.body.column(self.name_col).to_pylist()
        return [self.child(self.child_path(x), x) for x in names]
