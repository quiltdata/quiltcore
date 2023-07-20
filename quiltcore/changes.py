from itertools import groupby

from pathlib import Path

from yaml import dump

from .builder import Builder
from .delta import Delta
from .header import Header
from .manifest import Manifest
from .resource import Resource
from .resource_key import ResourceKey


class Changes(ResourceKey):
    """
    Track Changes to a new or existing Manifest
    Add a file: put(path, action="add", key="filename.txt", prefix="./")
    Use 'get' and 'list' to return the Deltas
    Create Manifest in scratch directory

    Optional: track changes to a directory?
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

    def grouped_rows(self) -> dict[str, list[dict]]:
        rows = [row for delta in self.keystore.values() for row in delta.to_dicts()]
        rows = sorted(rows, key=lambda row: row[Delta.KEY_ACT])
        grouped = {k: list(v) for k,v in groupby(rows, lambda row: row[Delta.KEY_ACT])}
        return grouped


    def to_manifest(self, **kwargs) -> Manifest:
        """
        Return a Manifest for this change set.
        Options:
        * user_meta: package-level metadata
        * msg: commit message

        1. Get rows from each Delta (multiple if a directory)
        1. Create Entry for each row
        2. Create a Manifest from the entries (adding metadata if present)

        """
        grouped = self.grouped_rows()
        adds = grouped.get(Delta.KEY_ADD)
        build = Builder(self.path, adds, kwargs, rm=grouped.get(Delta.KEY_RM), **self.args)  # type: ignore
        return build.to_manifest()
