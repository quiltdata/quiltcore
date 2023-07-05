from pathlib import Path

from .resource_path import ResourcePath


class Namespace(ResourcePath):
    """
    Namespacespace of Manifests by Hash
    list/get returns a specific Manifest
    """
    TAG_DEFAULT = "latest"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.versions = kwargs["versions"]

    def hash(self, tag: str = TAG_DEFAULT) -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        hash = self.hash(key)
        return self.versions / hash
