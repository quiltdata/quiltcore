from pathlib import Path

import logging
import pyarrow as pa  # type: ignore
import pyarrow.compute as pc  # type: ignore
import pyarrow.json as pj  # type: ignore
from typing_extensions import Self
from upath import UPath

from .resource_key import ResourceKey


class Manifest(ResourceKey):
    """
    In-memory representation of a serialized package manifest.
    list/get returns Entry with Path to the Place data actually lives
    """

    DEFAULT_HASH_TYPE = "SHA256"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        try:
            self.body = self.setup_table()
        except FileNotFoundError:
            logging.warning(f"Manifest not found: {path}")
        self.kName = self.cf.get_str("quilt3/name", "logical_key")
        self.kPlaces = self.cf.get_str("quilt3/places", "physical_keys")
        self.kSize = self.cf.get_str("quilt3/size", "size")
        self.kHash = self.cf.get_str("quilt3/hash", "hash")
        self.defaultHash = self.cf.get_str("quilt3/hash_type", self.DEFAULT_HASH_TYPE)   

    def setup_table(self) -> pa.Table:
        """
        Read the manifest into a pyarrow Table.
        Extract header values into attributes.
        Return the Table without header row and columns
        """
        with self.path.open(mode="rb") as fi:
            self.table = pj.read_json(fi)
        first = self.table.take([0]).to_pydict()
        headers = self.cf.get_dict("quilt3/headers")
        keys = list(headers.keys())
        for header in keys:
            setattr(self, header, first[header][0])
        return self.table.drop_columns(keys).slice(1)

    #
    # Private Methods for child resources
    #

    def child_names(self, **kwargs) -> list[str]:
        """List all child resources."""
        names = self.body.column(self.kName).to_pylist()
        return names

    def child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        # TODO: cache to avoid continually re-calcluating
        rows = self.body.filter(pc.field(self.kName) == key)
        if rows.num_rows == 0:
            raise KeyError(f"Key [{key}] not found in {self.kName} of {self.path}")
        row = rows.to_pydict()
        place = row[self.kPlaces][0][0]
        row[self.kPath] = place
        return row
