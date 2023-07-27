from pathlib import Path

from yaml import dump

from .delta import Delta
from .resource import Resource
from .resource_key import ResourceKey


class Changes(ResourceKey):
    """
    Track Changes to a new or existing Manifest
    Add a file or directory: post(path, action="add", key="filename.txt", prefix="./")
    Use 'get' and 'list' to return the Deltas
    Create Manifest in self.path
    """

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Non-directory path: {path}")
        self.keystore = {}

    def __str__(self):
        return dump(self.to_dict())

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.keystore.items()}

    #
    # Mutating Changes
    #

    def post(self, path: Path, **kwargs) -> Resource:
        """
                Create and track a Delta resource for this Path
                Options:
                * action: add [default], rm
                * key: defaults to filename
                * prefix: pre-pended to key if non-empty
        .
        """
        delta = Delta(path, **kwargs)
        self.keystore[delta.name] = delta
        return delta

    def delete(self, key: str, **kwargs) -> None:
        """Delete the key from this change set"""
        if key in self.keystore:
            del self.keystore[key]
            return
        raise KeyError(f"Key {key} not found in {self.keystore}")

    #
    # ResourceKey helper methods
    #

    def child(self, key: str, **kwargs) -> Delta:
        """Return a Delta by key. Raise KeyError if not found."""
        if key in self.keystore:
            return self.keystore[key]
        raise KeyError(f"Key {key} not found in {self.keystore}")

    def _child_names(self, **kwargs) -> list[str]:
        """Return keys for each change."""
        return list(self.keystore.keys())
