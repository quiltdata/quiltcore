from .header import Header
from .udg.node import Node
from .udg.folder import Folder
from .udg.tabular import Tabular
from .udg.types import List4, Multihash


from pathlib import Path


class FolderBuilder(Folder):
    """Convert modified Folder into a Manifest"""

    def __init__(self, path: Path, parent: Node, **kwargs):
        super().__init__(path.name, parent, **kwargs)
        self.head = Header(path, first=Header.First())
        self.update()

    def update(self):
        self.body4 = [self.dict4_from_path(f) for f in self.values()]

    def _list4(self) -> List4:
        """Return a list4 of the manifest."""
        return [self.head.to_dict4()] + self.body4

    def to_bytes(self) -> bytes:
        hashable = self.head.q3hash()
        for dict4 in self.body4:
            hashable += self.q3hash_from_hash(dict4.multihash)
        return hashable.encode("utf-8")

    def commit(self, message: str = "Updated", user_meta: dict = {}) -> Multihash:
        """Commit the changes to the manifest."""
        setattr(self.head, self.K_MESSAGE, message)
        if user_meta:
            setattr(self.head, self.K_USER_META, user_meta)
        self.update()
        return self.hash()

    def save_to(self, namespace: Node, **kwargs) -> Path:
        """Create manifest at path in namespace."""
        root = namespace.path
        root.mkdir(parents=True, exist_ok=True)
        base = root / self.q3hash()
        path = Tabular.Write4(self._list4(), base)
        return path
