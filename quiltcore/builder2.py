from .udg.header import Header
from .udg.node import Node
from .udg.folder import Folder
from .udg.verifiable import VerifyDict
from .udg.types import List4, Multihash


from pathlib import Path


class FolderBuilder(Folder):
    """Convert modified Folder into a Manifest"""

    def __init__(self, path: Path, parent: Node, **kwargs):
        super().__init__(path.name, parent, **kwargs)
        self.path = path
        self.header: Header | None = None
        self.body4: list | None = None

    def update(self):
        self.body4 = self.to_list4(self.path)

    def list4(self) -> List4:
        """Return a list4 of the manifest."""
        assert self.body4 is not None
        assert self.header is not None
        return [self.header.to_dict4()] + self.body4

    def to_bytes(self) -> bytes:
        assert isinstance(self.body4, list)
        assert isinstance(self.header, Header)
        header_dict = VerifyDict(self.cf, self.header.hashable_dict())
        hashable = header_dict.q3hash()
        for dict4 in self.body4:
            hashable += self.q3hash_from_hash(dict4.multihash)
        return hashable.encode("utf-8")

    def commit(self, message: str = "Updated", user_meta: dict = {}) -> Multihash:
        """Commit the changes to the manifest."""
        assert isinstance(self.parent, Node)
        self.header = Header.FromMessage(message)
        if user_meta:
            setattr(self.header, self.K_USER_META, user_meta)
        self.update()
        return self.hash()
