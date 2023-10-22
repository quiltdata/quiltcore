import logging

from pathlib import Path

from .domain import Domain
from .manifest import Manifest
from .udg.folder import Folder
from .udg.tabular import Tabular
from .udg.types import List4

Tag = str


class Namespace(Folder):
    """
    Namespace of Manifests by Hash
    list/get returns a specific Manifest
    """

    SEP = "/"
    HASH_LEN = 64
    Q3HASH_KEY = "hash"
    K_SAVE = "save"

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        assert isinstance(self.parent, Domain)
        self.manifests = self._setup_dir(self.parent.base, "manifests")

    #
    # GET based on hash
    #

    def read_hash_from_tag(self, key: Tag = Domain.TAG_DEFAULT) -> str:
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
        hash = self.read_hash_from_tag(key)
        parquet_hash = Tabular.ParquetHash(hash)
        logging.debug(f"Namespace2._get[{key}]: {hash} -> {parquet_hash}")
        return super()._get(hash)

    #
    # PUT based on tag
    #

    def _valid(self, options: dict) -> bool:
        """TODO: Validate workflow before setting 'latest' tag."""
        return True

    def put(self, list4: List4, top_hash: str, **options) -> Tag:
        """Store a manifest under this namespace."""
        logging.debug(f"Namespace2.put[{top_hash}]")
        tag = self.tag(top_hash, **options)
        self._save(list4, top_hash)
        return tag

    def tag(self, hash: str, **options) -> Tag:
        tag = self.Now()
        self._put(tag, hash)
        if self._valid(options):
            self._put(Domain.TAG_DEFAULT, hash)
        return tag

    def _put(self, tag: Tag, hash: str):
        """Put a hash into the namespace via a tag."""
        hash_file = self.path / tag
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(hash)
        logging.debug(f"Namespace2.put[{tag}]: {hash_file}")

    def _save(self, list4: List4, top_hash: str):
        manifest_path = self.manifests / top_hash
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        Tabular.WriteParquet(list4, manifest_path)

    #
    # PULL via relaxation
    #

    def relax_params(self) -> dict:
        domain = self.parent
        assert isinstance(domain, Domain)
        return {
            "manifests": self.manifests,
            "namespace": self,
            "store": domain.store,
            "package_path": domain.package_path(self.name),
        }

    def pull(self, manifest: Manifest, install_dir: Path, **flags) -> Tag:
        """PUT relaxed manifest into the namespace."""
        assert isinstance(manifest, Manifest)
        if not flags.get("no_copy", False):
            manifest = manifest.relax(install_dir, self.relax_params())
            assert manifest is not None
        return self.tag(manifest.q3hash())
