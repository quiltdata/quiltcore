from pathlib import Path

from .resource import Resource


class Namespace(Resource):
    """
    Namespacespace of Manifests by Hash
    list/get returns a specific Manifest
    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.versions = kwargs["versions"]

    def hash(self, tag: str = "latest") -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        hash = self.hash(key)
        return self.versions / hash
