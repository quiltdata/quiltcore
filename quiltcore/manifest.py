from pathlib import Path
from upath import UPath

import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore
import pyarrow.json as pj  # type: ignore

from .resource import CoreResource


class CoreManifest(CoreResource):
    """In-memory representation of a serialized package manifest."""

    def __init__(self, path: Path, parent: CoreResource | None = None):
        super().__init__(path, parent)
        with path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
            self.body = self.setup()
            self.name_col = self.config.get_str("schema/name", "logical_key")
            self.loc_col = self.config.get_str("schema/location", "physical_keys")

    def setup(self) -> pa.Table:
        first = self.table.take([0]).to_pydict()
        headers = self.get_dict("schema/headers")
        keys = list(headers.keys())
        for key in keys:
            setattr(self, key, first[key][0])
        return self.table.drop_columns(keys).slice(1)
        
    def child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        expr = pc.field(self.name_col) == key
        rows = self.body.filter(expr)
        if rows.num_rows == 0:
            raise KeyError(f"Key {key} not found in {self.name_col} of {self.path}")
        row = rows.to_pydict()
        loc = row[self.loc_col][0][0]
        return UPath(loc)

    def list_gen(self):
        """Return a generator of child paths."""
        names = self.body.column(self.name_col).to_pylist()
        return [self.child_path(name) for name in names]
