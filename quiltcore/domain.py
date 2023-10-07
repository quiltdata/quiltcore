import logging
import datetime
import os

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
        scheme, path = uri.split(cls.URI_SPLIT)
        return quilt[scheme][path]

    @classmethod
    def ToPath(cls, scheme, domain):
        if scheme == "file":
            return UPath(domain)
        uri = f"{scheme}{cls.URI_SPLIT}{domain}"
        logging.debug(f"Domain.ToPath: {uri}")
        return UPath(uri)

    @classmethod
    def FindStore(cls, next: Node) -> UPath:
        """Return the datastore path."""
        parent = next.parent
        if parent is None:
            raise ValueError("No parent for {self}")
        if isinstance(parent, Domain):
            return parent.store
        return cls.FindStore(parent)

    @staticmethod
    def TimeStamp() -> str:
        """Return a timestamp."""
        return datetime.datetime.now().isoformat()

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        self.store = self.ToPath(self.parent_name(), name)
        logging.debug(f"Domain.root: {self.store}")
        self.base = self._setup_dir(self.store, "config")
        self.path = self._setup_dir(self.base, "names")
        self.remotes = self._setup_dir(self.base, "remotes")
        self.is_mutable = kwargs.get(self.K_MUTABLE, False)
        self.data_yaml = Data(self.store)

    def pull(self, udi: UDI, dest: UPath | None = None, **kwargs):
        """Pull resource at the UDI into the domain."""
        assert self.is_mutable, "Can not pull into read-only Domain"
        path = dest or UPath(udi.package)
        self._track_lineage("pull", udi, path, **kwargs)
        return self.cf.AsStr(path)

    def _status(self, attrs: dict, **kwargs) -> dict:
        """Return the status dictionary for this UDI event."""
        status = {
            "timestamp": self.TimeStamp(),
            "user": os.getlogin(),
            **attrs,
            **kwargs,
        }
        return status

    def _track_lineage(self, action, udi: UDI, path: UPath, **kwargs):
        """Store the UDI in the domain."""
        dest = self.cf.AsStr(path)
        uri = udi.uri
        assert uri and isinstance(uri, str)
        # TODO: store hash and other udi attributes
        opts = self._status(udi.attrs, **kwargs)
        logging.debug(f"Domain._track_lineage: {action} {udi} {opts}")
        self.data_yaml.set(dest, uri, action, opts)
        self.data_yaml.save()
        return True

    def _remote_manifest(self, udi: UDI) -> Manifest2:
        """Return the manifest for the remote."""
        remote = Domain.FromURI(udi.uri)
        manifest = remote.get(udi.package)
        return manifest

    def _translate_manifest(self, manifest: Manifest2) -> Manifest2:
        """Translate the manifest to the local domain."""
        return manifest
