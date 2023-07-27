from pathlib import Path

from .delta import Delta
from .header import Header
from .manifest import Manifest
from .resource_key import ResourceKey
from .volume import Volume


class Builder(ResourceKey):
    """
    Create Entry resources for each row
    Calculate the hash
    Write a new manifest file
    Return the path
    """

    def __init__(self, path: Path, rows: list[dict], header: dict = {}, **kwargs):
        super().__init__(path, **kwargs)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"No directory path: {path}")

        self.head = Header(self.path, first=header)
        self.keystore = {row[Delta.KEY_NAM]: row for row in rows}
        self.removals = kwargs.get(Delta.KEY_RM, [])

    def write_manifest(self, **kwargs) -> Path:
        ns_name = (
            kwargs.get(self.KEY_NS)
            or self.args.get(self.KEY_NS)
            or f"unknown/{self.Now()}"
        )
        kwargs[self.KEY_NS] = ns_name
        if self.KEY_META in kwargs:
            user_meta = kwargs[self.KEY_META]
        if self.KEY_MSG in kwargs:
            message = kwargs[self.KEY_MSG]
        return self.path


    def _child_names(self, **kwargs) -> list[str]:
        """Return names of each child resource."""
        return list(self.keystore.keys())

    def _child_dict(self, key: str) -> dict:
        """Return the dict for a child resource."""
        return self.keystore[key]

    def _hash_multihash(self) -> str:
        return self._hash_manifest()

    def to_manifest(self, **kwargs) -> Manifest:
        """Create manifest file and return Manifest"""
        hash = self.hash_quilt3()
        path = self.path / hash
        Volume.WriteManifest(self.head, self.list(), path)  # type: ignore
        return Manifest(path, **self.args)
