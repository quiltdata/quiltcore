import logging
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from upath import UPath

from .domain import Domain
from .manifest import Manifest
from .udg.child import Child
from .udg.codec import Dict3, Dict4
from .udg.types import Types


class Entry(Child, Dict4, Types):
    """
    Represents a single row in a Manifest.
    Attributes:

    * path: Path (physical_key)
    * name: str (logical_key)
    * size: int
    * multihash: Multihash (str)
    * meta: dict
    """

    IS_REL = "./"
    IS_URI = ":/"

    @classmethod
    def GetQuery(cls, uri: str, key: str) -> str:
        """Extract key from URI query string."""
        query = urlparse(uri).query
        if not query:
            return ""
        qs = parse_qs(query)
        vlist = qs.get(key)
        return vlist[0] if vlist else ""

    def __init__(self, name: str, parent: Manifest, **kwargs):
        Child.__init__(self, name, parent, **kwargs)
        row = parent.table()[name]
        Dict4.__init__(self, **row.to_dict())

    def _setup(self):
        pass

    def extend_parent_path(self, key: str) -> Path:
        self.versionId = self.GetQuery(key, self.cf.K_VER)
        # Check if key is a URI or absolute path
        if self.IS_URI in key or Path(key).is_absolute():
            return UPath(key)
        if self.cf.IS_LOCAL.match(key) is not None:
            key = self.cf.IS_LOCAL.sub("", key)
        assert self.parent is not None, "Missing parent Manifest"
        namespace = self.parent.parent
        assert namespace is not None, "Missing grandparent Namespace"
        store = Domain.FindStore(namespace)
        if namespace.name not in str(store):
            store = store / namespace.name
        path = store / key
        return path

    #
    # Parse and unparse
    #

    def hashable_dict(self) -> dict:
        return self.cf.encode_hashable(self)

    def to_path(self, key: str) -> Path:
        dir = self.AsPath(key)
        dir.mkdir(parents=True, exist_ok=True)
        path = dir / self.name
        logging.debug(f"path: {path}")
        return path

    def to_dict3(self) -> Dict3:
        return self.cf.encode_dict4(self)

    #
    # Public Methods
    #

    # TODO: Need to rethink `install` since we do not pass Paths
    # Should this really be into a new Domain?

    def install(self, dest: str, **kwargs) -> "Entry":
        """Copy contents of resource's path into `dest` directory."""
        path = self.to_path(dest)
        path.write_bytes(self.to_bytes())  # for binary files
        assert isinstance(self.parent, Manifest)
        clone = Entry(self.name, self.parent)
        logging.debug(f"clone[{type(path)}]: {path.stat()}")
        clone.args[self.cf.K_PLC] = self.cf.AsString(path)
        return clone
