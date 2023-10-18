from pathlib import Path
from typing import Iterator

from .child import Child
from .node import Node


class Folder(Child):
    KEY_DIR = "quilt3/dirs/"
    KEY_GLOB = "glob"
    KEY_RECURSE = "recurse"
    DEFAULT_GLOB = "*"

    def __init__(self, name: str, parent: Node, **kwargs):
        super().__init__(name, parent, **kwargs)

    def _setup(self):
        super()._setup()
        self.glob = self.param(self.KEY_GLOB, self.DEFAULT_GLOB)
        self.recurse = self.param(self.KEY_RECURSE, "")

    def _setup_dir(self, path: Path, key: str) -> Path:
        """Form dir and create if it does not exist."""
        dir = path / self.cf.get_path(self.KEY_DIR + key)
        if not dir.exists():
            dir.mkdir(parents=True, exist_ok=True)
        return dir

    def __iter__(self) -> Iterator[str]:
        gen = self.path.rglob(self.glob) if self.recurse else self.path.glob(self.glob)
        return (str(x.relative_to(self.path)) for x in gen)
