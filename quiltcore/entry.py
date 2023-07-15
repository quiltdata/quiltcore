import logging
from copy import copy
from pathlib import Path

from .resource import Resource
from .resource_key import ResourceKey


class Entry(ResourceKey):
    """
    Represents a single row in a Manifest.
    Attributes:

    * name: str (logical_key)
    * path: Path (physical_key)
    * size: int
    * hash: str[multihash]
    * metadata: object

    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self._setup(kwargs)

    #
    # Parse and unparse
    #

    def get_value(self, row: dict, key: str):
        logging.debug(f"get_value: {key} from {row}")
        value = row.get(key, None)
        return value[0] if value else None

    def _setup(self, row: dict):
        self.name = self.get_value(row, self.kName) or self.path.name
        self.meta = self.get_value(row, self.kMeta)
        hash = self.get_value(row, self.kHash) or {}
        self._setup_hash(hash)  # type: ignore
        self.size = self.get_value(row, self.kSize)
        if not self.size:
            self.size = self.path.stat().st_size

    def to_row(self) -> dict:
        row = {
            self.kName: self.encode(self.name),
            self.kPlaces: [self.encode(str(self.path))],
            self.kSize: self.size,
            self.kHash: {"value": self.hash, "type": self.DEFAULT_HASH_TYPE},
            self.kMeta: self.meta,
        }
        return row

    def get(self, key: str, **kwargs) -> Resource:
        """Copy contents of resource's path into _key_ directory."""
        dir = self.AsPath(key)
        dir.mkdir(parents=True, exist_ok=True)
        path = dir / self.name
        logging.debug(f"path: {path}")
        path.write_bytes(self.to_bytes())  # for binary files
        clone = copy(self)
        clone.path = path.resolve()
        clone.args = kwargs
        logging.debug(f"clone: {clone}")

        return clone
