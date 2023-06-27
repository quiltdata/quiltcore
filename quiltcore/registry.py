from pathlib import Path

from .config import CoreConfig
from .manifest import CoreManifest

class CoreRegistry:
    def __init__(self, root: Path):
        self.params = CoreConfig()
        self.root = root
        self.config = root / self.params.get('dirs/config')
        self.names = self.config / self.params.get('dirs/names')
        self.versions = self.config / self.params.get('dirs/versions')

    def list(self) -> list:
        """List all package names in the registry."""
        gen = self.names.glob('*/*')
        return list(gen)
    
    def get(self, hash: str) -> CoreManifest:
        """Get a specific package manifest by hash."""
        version = self.versions / hash
        return CoreManifest.FromPath(version)

    def get_hash(self, name: str, tag: str = "latest") -> str:
        hash_file = self.names / name / tag
        return hash_file.read_text()