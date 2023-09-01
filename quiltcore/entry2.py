import logging
from pathlib import Path
from upath import UPath

from .domain import Domain
from .resource import Resource
from .udg.codec import Dict3, asdict
from .udg.child import Child
from .manifest2 import Manifest2


class Entry2(Child, Resource):
    """
    Represents a single row in a Manifest.
    Attributes:

    * path: Path (physical_key)
    * name: str (logical_key)
    * size: int
    * multihash: Multihash (str)
    * meta: dict

    """

    def __init__(self, name: str, parent: Manifest2, **kwargs):
        super().__init__(name, parent, **kwargs)
        row = parent.table().get_dict4(name)
        self.multihash = row.multihash or self._multihash_contents()
        self.size = row.size or self.path.stat().st_size
        self.meta = row.metadata or {}


    def _setup(self):
        pass

    def extend_parent_path(self, key: str) -> Path:
        if self.IS_REL not in key:
            return UPath(key)
        if self.IS_LOCAL.match(key) is not None:
            key = self.IS_LOCAL.sub("", key)
        path = Domain.FindStore(self) / key
        logging.debug(f"{key} -> {path} [{path.absolute()}]")
        return path

    #
    # Parse and unparse
    #

    def to_dict3(self) -> Dict3:
        row = self.cf.encode(self)
        # row[self.KEY_PATH] = self.path
        return row

    def hashable_dict(self) -> dict:
        if not self.multihash or not self.size:
            raise ValueError(f"Missing hash or size: {self}")
        hashable = {
            self.cf.config("map")["name"]: self.name,
            self.KEY_HSH: self.cf.encode_hash(self.multihash),
            self.KEY_SZ: self.size,
        }
        hashable[self.KEY_META] = self.meta # or {}
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
        kwargs = asdict(self.to_dict3())
        clone = Entry2(key, **kwargs)
        logging.debug(f"clone[{type(path)}]: {path.stat()}")
        clone.args[self.cf.K_PLC] = self.cf.AsStr(path)
        return clone
