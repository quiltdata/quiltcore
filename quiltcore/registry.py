from pathlib import Path

from .config import CoreConfig


class CoreRegistry:
    def __init__(self, root: Path):
        self.params = CoreConfig()
        self.root = root
        self.config = root / self.params.get('config_dir')
        self.names = self.config / self.params.get('names_dir')
        self.versions = self.config / self.params.get('versions_dir')

    def list(self):
        return []