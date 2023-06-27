from pathlib import Path

from .config import CoreConfig

class CoreRegistry:
    def __init__(self, root: Path):
        self.params = CoreConfig()
        self.root = root
        self.config = root / self.params.get('dirs/config')
        self.names = self.config / self.params.get('dirs/names')
        self.versions = self.config / self.params.get('dirs/versions')

    async def list(self) -> list:
        """List all packages in the registry."""
        gen = self.names.glob('*/*')
        return list(gen)