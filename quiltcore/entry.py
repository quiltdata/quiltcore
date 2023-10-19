import logging
from pathlib import Path

from .resource import Resource
from .resource_key import ResourceKey
from .udg.codec import Dict3, Dict4


class Entry(ResourceKey, Dict4):
    """
    Represents a single row in a Manifest.
    Attributes:

    * path: Path (physical_key)
    * name: str (logical_key)
    * size: int
    * multihash: str[multihash]
    * meta: dict

    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        if path.is_dir():
            raise ValueError(f"Entry cannot be a directory: {path}")
        self.name = kwargs.get(self.cf.K_NAM, self.path.name)
        self.multihash: str = kwargs.get(self.KEY_MH, False) or self._hash_contents()
        self.size = kwargs.get(self.KEY_SZ, False) or self.path.stat().st_size
        self.meta = kwargs.get(self.KEY_META, None)

    def _hash_multihash(self) -> str:
        return self.multihash

    #
    # Parse and unparse
    #

    def to_dict3(self) -> Dict3:
        row = self.codec.encode_dict4(self)
        # row[self.KEY_PATH] = self.path
        return row

    def hashable_dict(self) -> dict:
        if not self.multihash or not self.size:
            raise ValueError(f"Missing hash or size: {self}")
        hashable = {
            self.codec.config("map")["name"]: self.name,
            self.KEY_HSH: self.codec.encode_hash(self.multihash),
            self.KEY_SZ: self.size,
        }
        hashable[self.KEY_META] = self.meta or {}
        return hashable

    def to_path(self, key: str) -> Path:
        dir = self.AsPath(key)
        dir.mkdir(parents=True, exist_ok=True)
        path = dir / self.name
        logging.debug(f"path: {path}")
        return path

    #
    # Public Methods
    #

    def install(self, key: str, **kwargs) -> Resource:
        """Copy contents of resource's path into _key_ directory."""
        path = self.to_path(key)
        path.write_bytes(self.to_bytes())  # for binary files
        kwargs = self.to_dict3().to_dict()
        clone = Entry(path.resolve(), **kwargs)
        logging.debug(f"clone[{type(path)}]: {path.stat()}")
        clone.args[self.cf.K_PLC] = self.codec.AsString(path)
        return clone
