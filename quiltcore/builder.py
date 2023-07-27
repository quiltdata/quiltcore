from pathlib import Path

from .changes import Changes
from .header import Header
from .manifest import Manifest
from .resource import Resource
from .resource_key import ResourceKey
from .volume import Volume


class Builder(ResourceKey):
    """
    Create Entry resources for each row
    Calculate the hash
    Write a new manifest file
    Return the path
    """

    def __init__(self, changes: Changes, **kwargs):
        super().__init__(changes.path)
        self.changes = changes
        self.head = Header(self.path, first=kwargs)

    def _hash_multihash(self) -> str:
        return self._hash_manifest()

    #
    # ResourceKey helper methods
    #

    def list(self, **kwargs) -> list[Resource]:
        """List all child resources."""
        nested_entries = [delta.list() for delta in self.changes.list()]
        return [entry for entries in nested_entries for entry in entries]

    def get(self, key: str, **kwargs) -> Resource:
        """Get a child resource by key."""
        delta = self.changes.get(key)
        children = delta.list()
        return children[0] 

    def post(self, path: Path, **kwargs) -> Resource:
        path = path or self.path
        hash = self.hash_quilt3()
        path = self.path / hash
        Volume.WriteManifest(self.head, self.list(), path)  # type: ignore
        return Manifest(path, **self.args)

