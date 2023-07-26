from pathlib import Path

from .resource_path import ResourcePath


class Namespace(ResourcePath):
    """
    Namespace of Manifests by Hash
    list/get returns a specific Manifest
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.manifests = kwargs[self.KEY_MAN]

    def hash(self, tag: str = ResourcePath.TAG_DEFAULT) -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def _child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        hash = self.hash(key)
        return self.manifests / hash
