from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

from .resource import Resource


class ResourceKey(Resource):
    """
    Get/List child resources by key in Manifest
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
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
    # Mapping methods: __getitem__, __iter__, and __len__.
    #

    def __getitem__(self, key: str) -> Resource:
        """Return a child resource by name."""
        return self.child(key)

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over child resource names."""
        return iter(self._child_names())

    def __len__(self) -> int:
        """Return the number of child resources."""
        return len(self._child_names())

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

    def hash_quilt3(self) -> str:
        """Return the hash of the source file."""
        mh = self._hash_multihash()
        hash_struct = self.codec.encode_hash(mh)
        return hash_struct["value"]

    def _hash_multihash(self) -> str:
        raise NotImplementedError("subclass must override")

    def _hash_contents(self) -> str:
        """Return the multihash of the source file."""
        return self.digest_bytes(self.to_bytes())

    def _hash_manifest(self) -> str:
        hashable = b""
        if hasattr(self, "head"):
            self.head.hashable()  # type: ignore
        for entry in self.list():
            hashable += entry.hashable()  # type: ignore
        return self.digest_bytes(hashable)

    #
    # Hash retreival
    #

    def legacy_verify(self, bstring: bytes) -> bool:
        """Verify that multihash digest of bytes match the multihash"""
        digest = self.digest_bytes(bstring)
        logging.debug(f"verify.digest: {digest}")
        if not hasattr(self, self.KEY_MH):
            raise ValueError("no hash found for {self}")
        return digest == getattr(self, self.KEY_MH)

    #
    # Concrete HTTP Methods
    #

    def getResource(self, key: str, **kwargs) -> "Resource":
        """Get a child resource by name."""
        return self.child(key, **kwargs)

    def list(self, **kwargs) -> list[Resource]:
        """List all child resources by name."""
        return [self.child(key, **kwargs) for key in self._child_names(**kwargs)]
