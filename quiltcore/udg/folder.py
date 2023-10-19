from pathlib import Path
from typing import Iterator

from .child import Child
from .node import Node
from .types import List4, Dict4


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

    def expand_path(self, file) -> Dict4:
        base = self.dict4_from_path(file)
        result = self.encode_date_dicts(base)
        assert isinstance(result, Dict4)
        return result

    def to_list4(self, folder: Path, glob=DEFAULT_GLOB) -> List4:
        """Generate to_dict4 for each file in path matching glob."""
        return [self.expand_path(file) for file in folder.rglob(glob)]
