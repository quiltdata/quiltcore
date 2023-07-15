from __future__ import annotations

import logging
from pathlib import Path

from multiformats import multihash

from .resource import Resource


class ResourceKey(Resource):
    """
    Get/List child resources by key in Manifest
    """

    MH_PREFIX = {
        "SHA256": "1220",
    }

    @classmethod
    def RowValue(cls, row: dict, key: str):
        logging.debug(f"get_value: {key} from {row}")
        value = row.get(key, None)
        return value[0] if value else None

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.defaultHash = self.cf.get_str("quilt3/hash_type", self.DEFAULT_HASH_TYPE)
        self.kHash = self.cf.get_str("quilt3/hash", "hash")
        self.kMeta = self.cf.get_str("quilt3/meta", "meta")
        self.kName = self.cf.get_str("quilt3/name", "logical_key")
        self.kPlaces = self.cf.get_str("quilt3/places", "physical_keys")
        self.kSize = self.cf.get_str("quilt3/size", "size")

    #
    # Abstract Methods for child resources
    #

    def _child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        return []

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        return {}

    #
    # Concrete Methods for child resources
    #

    def key_path(self, key: str, args: dict = {}) -> Path:
        """Return the Path for a child resource."""
        if self.KEY_PATH not in args:
            raise KeyError(f"Missing {self.KEY_PATH} in {args.keys()}")
        place = args[self.KEY_PATH]
        return self.AsPath(place)

    def child(self, key: str, **kwargs):
        """Return a child resource."""
        args = self._child_dict(key)
        path = self.key_path(key, args)
        merged = {**self.args, **args}
        return self.klass(path, **merged)


    #
    # Calculate and verify hash
    #

    def _setup_hash(self, opt: dict = {}):
        """Set or create hash attributes."""
        type = opt.get("type", self.defaultHash)
        hash_key = f"multihash/{type}"
        self.hash_type = self.cf.get_str(hash_key)
        self.hash_digest = multihash.get(self.hash_type)
        self.hash_prefix = self.MH_PREFIX[type]
        value = opt.get("value")
        self.multihash = self.hash_prefix + value if value else self.source_hash()
        self.hash = value if value else self.multihash.strip(self.hash_prefix)

    def source_hash(self) -> str:
        """Return the hash of the source file."""
        return self.digest(self.to_bytes())

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

    #
    # Concrete HTTP Methods
    #

    def get(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        return self.child(key, **kwargs)

    def list(self, **kwargs) -> list[Resource]:
        """List all child resources by name."""
        return [self.child(key, **kwargs) for key in self._child_names(**kwargs)]
