from pathlib import Path

from yaml import dump

from .delta import Delta
from .manifest import Manifest
from .resource import Resource
from .resource_key import ResourceKey


class Changes(ResourceKey):
    """
    Track Changes to a new or existing Manifest
    Add a file: put(path, action="add", key="filename.txt", prefix="./")
    Use 'get' and 'list' to return the Deltas

    Optional: track changes to a directory?
    """

    MANIFEST_FILE = "manifest.json"
    MANIFEST_KEY = "manifest"
    DEFAULT_MSG = f"Updated {ResourceKey.Now()}"

    @staticmethod
    def ScratchFile() -> Path:
        return Changes.TempDir(Changes.MANIFEST_FILE)

    @staticmethod
    def GetCache(path: Path) -> Path:
        if not path:
            return Changes.ScratchFile()
        if path.exists() and path.is_dir():
            return path / Changes.MANIFEST_FILE
        return path

    def __init__(self, path=None, **kwargs):
        cache = Changes.GetCache(path)
        super().__init__(cache, **kwargs)
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

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        delta = self.get_delta(key)
        return {self.kName: [delta.name], self.kPlaces: str(delta.path)}

    def get_delta(self, key: str, **kwargs) -> Delta:
        """Return a Delta by key. Raise KeyError if not found."""
        if key in self.keystore:
            return self.keystore[key]
        raise KeyError(f"Key {key} not found in {self.keystore}")

    def key_path(self, key: str, args: dict = {}) -> Path:
        """Return the Path for a child resource."""
        delta = self.get_delta(key)
        return delta.path

    def _child_names(self, **kwargs) -> list[str]:
        """Return keys for each change."""
        return list(self.keystore.keys())
    
    #
    # Create Manifest
    #

    def to_manifest(self, **kwargs) -> Manifest:
        """
        Return a Manifest for this change set.
        Options:
        * meta: package-level metadata
        * msg: commit message

        1. Get rows from each Delta (multiple if a directory)
        1. Create Entry for each row
        2. Create a Manifest from the entries (adding metadata if present)

        """
        meta = kwargs.get(self.KEY_META, {})
        msg = kwargs.get(self.KEY_MSG, self.DEFAULT_MSG)
        return Manifest(self.path, **self.args)
