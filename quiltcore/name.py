from pathlib import Path

from .resource import CoreResource


class CoreName(CoreResource):
    """Namespace of Manifests by Hash"""

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.values = kwargs["values"]

    def hash(self, tag: str = "latest") -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def child_path(self, key: str) -> Path:
        """Return the path for a child resource."""
        hash = self.hash(key)
        return self.values.path / hash
