import logging
from copy import copy
from pathlib import Path

from multiformats import multihash
from upath import UPath

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

    MH_PREFIX = {
        "SHA256": "1220",
    }

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.args = kwargs
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
        return {
            self.kName: self.name,
            self.kPlaces: [self.encode(self.path)],
            self.kSize: self.size,
            self.kHash: {"value": self.hash, "type": self.DEFAULT_HASH_TYPE},
            self.kMeta: self.meta,
        }

    #
    # Calculate and verify hash
    #

    def _setup_hash(self, opt: dict = {}):
        """Set or create hash attributes."""
        type = opt.get("type", self.defaultHash)
        hash_key = f"multihash/{type}"
        self.hash_type = self.cf.get_str(hash_key)
        self.hash_digest = multihash.get(self.hash_type)
        self.hash_prefix = Entry.MH_PREFIX[type]
        value = opt.get("value")
        self.multihash = self.hash_prefix + value if value else self.source_hash()
        self.hash = value if value else self.multihash.strip(self.hash_prefix)

    def source_hash(self) -> str:
        """Return the hash of the source file."""
        bytes = self.path.read_bytes()
        return self.digest(bytes)

    def digest(self, bstring: bytes) -> str:
        """Return the multihash digest of `bstring`"""
        digest = self.hash_digest.digest(bstring)
        digest.hex()
        return digest.hex()

    def verify(self, bstring: bytes) -> bool:
        """Verify that multihash digest of bytes match the multihash"""
        digest = self.digest(bstring)
        logging.debug(f"verify.digest: {digest}")
        return digest == self.multihash

    def get(self, key: str, **kwargs) -> Resource:
        """Copy contents of resource's path into _key_ directory."""
        dir = UPath(key)
        dir.mkdir(parents=True, exist_ok=True)
        path = dir / self.name
        logging.debug(f"path: {path}")
        path.write_bytes(self.path.read_bytes())  # for binary files
        clone = copy(self)
        clone.path = path.resolve()
        clone.args = kwargs
        logging.debug(f"clone: {clone}")

        return clone
