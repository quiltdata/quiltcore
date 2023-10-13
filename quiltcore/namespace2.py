import logging

from pathlib import Path

from .domain import Domain
from .manifest2 import Manifest2
from .udg.folder import Folder

Tag = str


class Namespace2(Folder):
    """
    Namespace of Manifests by Hash
    list/get returns a specific Manifest
    """

    SEP = "/"
    HASH_LEN = 64
    Q3HASH_KEY = "hash"
    TAG_DEFAULT = "latest"
    K_SAVE = "save"

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        assert isinstance(self.parent, Domain)
        self.manifests = self._setup_dir(self.parent.base, "manifests")

    #
    # GET based on hash
    #

    def get_q3hash(self, key: Tag = TAG_DEFAULT) -> str:
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
                # TODO: prefer Parquet if both present
        if hash is not None:
            return hash
        raise ValueError(f"Tag/Hash not found: {key}")

    def _get(self, key: Tag):
        hash = self.get_q3hash(key)
        return super()._get(hash)

    #
    # PUT based on tag
    #

    def _valid(self, options: dict) -> bool:
        """TODO: Validate workflow before setting 'latest' tag."""
        return True

    def put(self, manifest: Manifest2, **options) -> Tag:
        """Store a manifest under this namespace."""
        hash = manifest.q3hash()
        logging.debug(f"Namespace2.put: {hash}")
        tag = self.tag(hash, **options)
        self._save(manifest, hash)
        return tag

    def tag(self, hash: str, **options) -> Tag:
        tag = self.Now()
        self._put(tag, hash)
        if self._valid(options):
            self._put(self.TAG_DEFAULT, hash)
        return tag

    def _put(self, tag: Tag, hash: str):
        """Put a hash into the namespace via a tag."""
        hash_file = self.path / tag
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(hash)
        logging.debug(f"Namespace2.put[{tag}]: {hash_file}")

    def _save(self, manifest: Manifest2, hash: str):
        man_file = self.manifests / hash
        man_file.parent.mkdir(parents=True, exist_ok=True)
        man_file.write_bytes(manifest.to_bytes())

    #
    # PULL via relaxation
    #

    def pull(self, remote: Manifest2, install_dir: Path, **flags) -> Tag:
        """PUT relaxed manifest into the namespace."""
        assert isinstance(remote, Manifest2)
        if not flags.get("no_copy", False):
            remote = remote.relax(install_dir, self.manifests, self)
            assert remote is not None
        return self.put(remote)
