from pathlib import Path

from .manifest import CoreManifest
from .resource import CoreResource
from .values import CoreValues

class CoreName(CoreResource):

    def __init__(self, name: Path, parent: CoreValues):
        self.name = name
        self.values = parent

    def __repr__(self):
        return f"<CoreName {self.name}>"
    
    def __str__(self):
        return str(self.name)

    def list(self) -> list[Path]:
        """List all tags under this name."""
        gen = self.name.glob('*')
        return list(gen)

    def get(self, tag: str = "latest") -> CoreResource:
        """Get a specific Manifest by tag."""
        hash = self.get_hash(tag)
        return self.values.get(hash)

    def get_hash(self, tag: str = "latest") -> str:
        hash_file = self.name / tag
        return hash_file.read_text()