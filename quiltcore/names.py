import logging

from .domain import Domain
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
        assert isinstance(self.parent, Domain)
        self.manifests = self._setup_dir(self.parent.base, "manifests")
        print(f"manifests: {self.manifests}")

    def get_q3hash(self, key: str = TAG_DEFAULT) -> str:
        hash_file = self.path / key
        if hash_file.exists():
            return hash_file.read_text()
        logging.debug(f"tag not found: {hash_file}\ninterpet as hash: {key}")

        if len(key) == self.HASH_LEN:
            return key

        hash = None
        for match in self.manifests.rglob(f"{key}*"):
            if hash is None:
                hash = match.name
            else:
                raise ValueError(f"Multiple matches for hash: {key}")
        if hash is not None:
            return hash
        raise ValueError(f"Tag/Hash not found: {key}")

    def _get(self, key: str):
        hash = self.get_q3hash(key)
        return super()._get(hash)
