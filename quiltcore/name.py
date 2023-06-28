from pathlib import Path

from .manifest import CoreManifest
from .resource import CoreResource


class CoreName(CoreResource):
    """Namespace of Manifests by Hash"""

    def __init__(self, path: Path, parent: CoreResource):
        super().__init__(path, parent)
        self.values = parent

    def hash(self, tag: str = "latest") -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def child(self, path: Path, key: str = "") -> CoreManifest:
        """Return a child resource."""
        # return self.klass(path, self.child_parent(key))
        hash = self.hash(key)
        return CoreManifest(self.values.path / hash, self)
