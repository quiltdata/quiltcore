import logging
from pathlib import Path
from re import compile

from upath import UPath

from .domain import Domain
from .manifest2 import Manifest2
from .udg.child import Child


class Entry2(Child):
    """
    Represents a single row in a Manifest.
    Attributes:

    * path: Path (physical_key)
    * name: str (logical_key)
    * size: int
    * multihash: Multihash (str)
    * meta: dict
    """

    IS_LOCAL = compile(r"file:\/*")
    IS_REL = "./"
    IS_URI = ":/"

    @classmethod
    def AsPath(cls, key: str) -> Path:
        """Return a Path from a string."""
        if not isinstance(key, str):
            raise TypeError(f"[{key}]Expected str, got {type(key)}")
        return UPath(key, version_aware=True)

    def __init__(self, name: str, parent: Manifest2, **kwargs):
        super().__init__(name, parent, **kwargs)
        row = parent.table().get_dict4(name)
        self.path = self.extend_parent_path(row.place)
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

    def hashable_dict(self) -> dict:
        if not self.multihash or not self.size:
            raise ValueError(f"Missing hash or size: {self}")
        hashable = {
            self.cf.config("map")["name"]: self.name,
            self.cf.K_HASH: self.cf.encode_hash(self.multihash),
            self.cf.K_SIZE: self.size,
        }
        hashable[self.cf.K_META] = self.meta  # or {}
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

    # TODO: Need to rethink `install` since we do not pass Paths
    # Should this really be into a new Domain?

    def install(self, dest: str, **kwargs) -> "Entry2":
        """Copy contents of resource's path into `dest` directory."""
        path = self.to_path(dest)
        path.write_bytes(self.to_bytes())  # for binary files
        assert isinstance(self.parent, Manifest2)
        clone = Entry2(self.name, self.parent)
        logging.debug(f"clone[{type(path)}]: {path.stat()}")
        clone.args[self.cf.K_PLC] = self.cf.AsStr(path)
        return clone
