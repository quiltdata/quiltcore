from pathlib import Path

import pyarrow as pa  # type: ignore
import pyarrow.json as pj  # type: ignore``

from .resource import CoreResource


class CoreManifest(CoreResource):
    """In-memory representation of a serialized package manifest."""

    def __init__(self, path: Path, parent: CoreResource | None = None):
        super().__init__(path, parent)
        with path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
            self.body = self.setup()

    def setup(self) -> pa.Table:
        first = self.table.take([0]).to_pydict()
        print(f"first: {first}")
        headers = self.get_dict("schema/headers")
        print(f"headers: {headers}")
        keys = list(headers.keys())
        print(f"keys: {keys}")
        for key in keys:
            print(f"key: {key} <- {first}")
            setattr(self, key, first[key][0])
        return self.table.drop_columns(keys).slice(1)
        
            

