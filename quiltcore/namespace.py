from pathlib import Path

from .resource_path import ResourcePath


class Namespace(ResourcePath):
    """
    Namespace of Manifests by Hash
    list/get returns a specific Manifest
    """

    SEP = "/"
    HASH_LEN = 64

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.manifests = kwargs[self.KEY_MAN]
        self.name = self.pkg_name()

    def hash(self, tag: str = ResourcePath.TAG_DEFAULT) -> str:
        hash_file = self.path / tag
        return hash_file.read_text()

    def _child_path(self, key: str, **kwargs) -> Path:
        """Return the path for a child resource."""
        hash = kwargs.get(self.KEY_HSH) or self.hash(key)
        if len(hash) == self.HASH_LEN:
            return self.manifests / hash
        for match in self.manifests.glob(f"{hash}*"):
            return match
        raise ValueError(f"hash must be {self.HASH_LEN} chars long")

    def pkg_name(self) -> str:
        return self.SEP.join(self.path.parts[-2:])
