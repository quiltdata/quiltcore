import datetime
import logging
import os

from pathlib import Path
from upath import UPath

from .factory import quilt
from .manifest2 import Manifest2
from .udg.folder import Folder
from .udg.node import Node
from .yaml.data import Data
from .yaml.udi import UDI


class Domain(Folder):
    K_MUTABLE = "mutable"
    URI_SPLIT = "://"

    @classmethod
    def FromURI(cls, uri):
        """Return a domain from a URI."""
        scheme, path = uri.split(cls.URI_SPLIT)
        print(f"Domain.FromURI: {scheme} {cls.URI_SPLIT} {path} -> {uri}")
        return quilt[scheme][path]

    @classmethod
    def FindStore(cls, next: Node) -> Path:
        """Return the datastore path."""
        parent = next.parent
        if parent is None:
            raise ValueError("No parent for {self}")
        if isinstance(parent, Domain):
            return parent.store
        return cls.FindStore(parent)

    @classmethod
    def GetRemoteManifest(cls, udi: UDI) -> Manifest2:
        """Return the manifest for the UDI."""
        domain = cls.FromURI(udi.registry)
        namespace = domain.get(udi.package)
        tag = udi.attrs.get(udi.K_TAG, namespace.TAG_DEFAULT)
        manifest = namespace.get(tag)
        assert manifest is not None, f"Manifest not found for tag[{tag}]: {udi}"
        return manifest

    @staticmethod
    def TimeStamp() -> str:
        """Return a timestamp."""
        return datetime.datetime.now().isoformat()

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        print(f"Domain.__init__: {name}, {parent}, {kwargs}")
        self.store = self.cf.ToPath(self.parent_name(), name)
        print(f"Domain.store: {self.store}")
        assert self.store.exists(), f"Domain store does not exist: {self.store}"
        logging.debug(f"Domain.root: {self.store}")
        self.base = self._setup_dir(self.store, "config")
        self.path = self._setup_dir(self.base, "names")
        self.remotes = self._setup_dir(self.base, "remotes")
        self.is_mutable = kwargs.get(self.K_MUTABLE, False)
        self.data_yaml = Data(self.store)

    def pull(self, udi: UDI, install_folder: UPath | None = None, **kwargs):
        """Pull resource at the UDI into the domain at path."""
        assert self.is_mutable, "Can not pull into read-only Domain"
        no_copy = kwargs.get("no_copy", False)
        remote = self.GetRemoteManifest(udi)
        namespace = self.get(udi.package)
        assert namespace is not None
        install_dir = install_folder or self.store / udi.package
        install_dir.mkdir(parents=True, exist_ok=True)
        assert install_dir.is_dir(), f"install_dir not a directory: {install_dir}"
        self._track_lineage("pull", udi, install_dir, **kwargs)
        namespace.pull(remote, install_dir, no_copy=no_copy)
        return install_dir

    def _status(self, attrs: dict, **kwargs) -> dict:
        """Return the status dictionary for this UDI event."""
        status = {
            "timestamp": self.TimeStamp(),
            "user": os.environ.get("USER", "unknown"),
            **attrs,
            **kwargs,
        }
        return status

    def _track_lineage(self, action, udi: UDI, path: Path, **kwargs):
        """Store the UDI in the domain."""
        opts = self._status(udi.attrs, **kwargs)
        logging.debug(f"Domain._track_lineage: {action} {udi} {path} {opts}")
        uri = udi.uri
        assert uri and isinstance(uri, str)
        folder = str(path)
        # TODO: store hash and other udi attributes
        self.data_yaml.set(folder, uri, action, opts)
        self.data_yaml.save()
        return folder
