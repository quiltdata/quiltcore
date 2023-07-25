from __future__ import annotations

import logging
from json import JSONEncoder
from pathlib import Path

from .resource import Resource
from .yaml.codec import Codec


class ResourceKey(Resource):
    """
    Get/List child resources by key in Manifest
    """

    ENCODE = JSONEncoder(sort_keys=True, separators=(",", ":"), default=str).encode

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.codec = Codec()
        self.headers = self.cf.get_dict("quilt3/headers")

    #
    # Abstract Methods for child resources
    #

    def _child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        raise NotImplementedError

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        raise NotImplementedError

    #
    # Concrete Methods for child resources
    #

    def key_path(self, key: str, args: dict = {}) -> Path:
        """Return the Path for a child resource."""
        return self.AsPath(args[self.cf.K_PLC])

    def child(self, key: str, **kwargs):
        """Return a child resource."""
        args = self._child_dict(key)
        path = self.key_path(key, args)
        merged = {**self.args, **args}
        self.CheckPath(path)
        return self.klass(path, **merged)

    #
    # Hash creation
    #

    def digest(self, bstring: bytes) -> str:
        """Return the multihash digest of `bstring`"""
        return self.codec.digest(bstring)

    def hash_quilt3(self) -> str:
        """Return the hash of the source file."""
        mh = self._hash_multihash()
        hash_struct = self.codec.encode_hash(mh)
        return hash_struct["value"]

    def _hash_multihash(self) -> str:
        raise NotImplementedError("subclass must override")

    def _hash_path(self) -> str:
        """Return the multihash of the source file."""
        return self.digest(self.to_bytes())

    def _hash_manifest(self) -> str:
        hashable = b""
        if hasattr(self, "head"):
            self.head.hashable()  # type: ignore
        for entry in self.list():
            hashable += entry.hashable()  # type: ignore
        return self.digest(hashable)

    #
    # Hash retreival
    #

    def to_hashable(self) -> dict:
        raise NotImplementedError

    def hashable(self) -> bytes:
        source = self.to_hashable()
        return self.ENCODE(source).encode("utf-8")  # type: ignore

    def verify(self, bstring: bytes) -> bool:
        """Verify that multihash digest of bytes match the multihash"""
        digest = self.digest(bstring)
        logging.debug(f"verify.digest: {digest}")
        if not hasattr(self, self.KEY_MH):
            raise ValueError("no hash found for {self}")
        return digest == getattr(self, self.KEY_MH)

    #
    # Concrete HTTP Methods
    #

    def get(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        return self.child(key, **kwargs)

    def list(self, **kwargs) -> list[Resource]:
        """List all child resources by name."""
        return [self.child(key, **kwargs) for key in self._child_names(**kwargs)]
