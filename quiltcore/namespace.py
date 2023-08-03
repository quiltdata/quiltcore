from pathlib import Path

from .resource_path import ResourcePath


class Namespace(ResourcePath):
    """
    Namespace of Manifests by Hash
    list/get returns a specific Manifest
    """
    SEP = "/"

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.manifests = kwargs[self.KEY_MAN]
        self.name = self.pkg_name()

    def hash(self, tag: str = ResourcePath.TAG_DEFAULT) -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def _child_path(self, key: str, **kwargs) -> Path:
        """Return the path for a child resource."""
        # TODO: match on partial hashes
        hash = self.hash(key)
        return self.manifests / hash

    def pkg_name(self) -> str:
        return self.SEP.join(self.path.parts[-2:])