from pathlib import Path

from .config import CoreConfig

class CoreRegistry:    
    def __init__(self, root: Path):
        self.root = root
        self.conf = CoreConfig()
