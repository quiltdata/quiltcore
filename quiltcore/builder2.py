from .header import Header
from .udg.node import Node
from .udg.folder import Folder
from .udg.types import List4, Multihash


from pathlib import Path


class FolderBuilder(Folder):
    """Convert modified Folder into a Manifest"""

    def __init__(self, path: Path, parent: Node, **kwargs):
        super().__init__(path.name, parent, **kwargs)
        self.path = path
        self.head: Header | None = None
        self.body4: list | None = None

    def update(self):
        self.body4 = [self.dict4_from_path(Path(f)) for f in self.keys()]

    def list4(self) -> List4:
        """Return a list4 of the manifest."""
        assert self.body4 is not None
        assert self.head is not None
        return [self.head.to_dict4()] + self.body4

    def to_bytes(self) -> bytes:
        assert isinstance(self.body4, list)
        assert isinstance(self.head, Header)
        hashable = self.head.q3hash()
        for dict4 in self.body4:
            hashable += self.q3hash_from_hash(dict4.multihash)
        return hashable.encode("utf-8")

    def commit(self, message: str = "Updated", user_meta: dict = {}) -> Multihash:
        """Commit the changes to the manifest."""
        self.head = Header(self.path, first=Header.First(message))
        if user_meta:
            setattr(self.head, self.K_USER_META, user_meta)
        self.update()
        return self.hash()
