from pathlib import Path

from .changes import Changes
from .header import Header
from .manifest import Manifest
from .resource import Resource
from .resource_key import ResourceKey


class Builder(ResourceKey):
    """
    Create Entry resources for each row
    Calculate the hash
    Write a new manifest file
    Return the path
    """

    @classmethod
    def MakeManifest(cls, changes: Changes, pkg_meta: dict) -> Manifest:
        build = cls(changes, **pkg_meta)
        man = build.post(changes.path)
        if not isinstance(man, Manifest):
            raise ValueError(f"Expected Manifest {man} not {type(man)}")
        return man

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
        """List all child entries."""
        nested_entries = [delta.list() for delta in self.changes.list()]
        return [entry for entries in nested_entries for entry in entries]

    def get(self, key: str, **kwargs) -> Resource:
        """Get a child entry by key."""
        delta = self.changes.get(key)
        children = delta.list()
        return children[0]

    def post(self, path: Path, **kwargs) -> Resource:
        path = path or self.path
        hash = self.hash_quilt3()
        path = self.path / hash
        rows = self.list()
        if len(rows) == 0:
            raise ValueError(f"Cannot post empty manifest: {self.changes}")
        Manifest.WriteToPath(self.head, self.list(), path)  # type: ignore
        return Manifest(path, **kwargs)
