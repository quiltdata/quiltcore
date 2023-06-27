from pathlib import Path

from .config import CoreConfig

class CoreRegistry:
    def __init__(self, root: Path):
        self.params = CoreConfig()
        self.root = root
        self.config = root / self.params.get('config_dir')
        self.names = self.config / self.params.get('names_dir')
        self.versions = self.config / self.params.get('versions_dir')

    async def list(self) -> list:
        """List all packages in the registry."""
        gen = self.names.glob('*/*')
        return list(gen)