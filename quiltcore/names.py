from pathlib import Path

from .udg.folder import Folder


class Names(Folder):
    """
    Namespace of Manifests by Hash
    list/get returns a specific Manifest
    """

    SEP = "/"
    HASH_LEN = 64
    Q3HASH_KEY = "hash"
    TAG_DEFAULT = "latest"

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        self.manifests = self._setup_dir(self.path, "manifests")

    def read_q3hash(self, tag: str = TAG_DEFAULT) -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def _child_path(self, key: str, **kwargs) -> Path:
        """Return the path for a child resource."""
        hash = kwargs.get(self.Q3HASH_KEY) or self.read_q3hash(key)
        if len(hash) == self.HASH_LEN:
            return self.manifests / hash
        for match in self.manifests.glob(f"{hash}*"):
            return match
        raise ValueError(f"hash must be {self.HASH_LEN} chars long")

    def pkg_name(self) -> str:
        return self.SEP.join(self.path.parts[-2:])
