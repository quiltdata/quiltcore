import logging
from typing import Iterator

from .node import Node
from .child import Child

from pathlib import Path

class Folder(Child):
    KEY_DIR = "quilt3/dirs/"
    KEY_GLOB = "glob"

    def __init__(self, name: str, parent: Node, **kwargs):
        super().__init__(name, parent, **kwargs)

    def _setup(self):
        super()._setup()
        self.glob = self.param(self.KEY_GLOB, "*")

    def _setup_dir(self, path: Path, key: str) -> Path:
        """Form dir and create if it does not exist."""
        dir = path / self.cf.get_path(self.KEY_DIR + key)
        print(f"Folder._setup_dir[{key}]: {dir}")
        if not dir.exists():
            dir.mkdir(parents=True, exist_ok=True)
        return dir

    def __iter__(self) -> Iterator[str]:
        gen = self.path.rglob(self.glob)
        return (str(x) for x in gen)
