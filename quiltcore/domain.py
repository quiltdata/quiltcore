import datetime
import logging
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

    @classmethod
    def GetManifest(cls, udi: UDI) -> Manifest2:
        """Return the manifest for the UDI."""
        domain = cls.FromURI(udi.registry)
        namespace = domain.get(udi.package)
        tag = udi.attrs.get(udi.K_TAG, namespace.TAG_DEFAULT)
        manifest = namespace.get(tag)
        return manifest

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
        prefix = self.cf.AsStr(path)
        self._track_lineage("pull", udi, prefix, **kwargs)
        remote = self.GetManifest(udi)
        namespace = self.get(udi.package)
        assert namespace is not None
        namespace.pull(remote, prefix, no_copy=True)
        return prefix

    def _status(self, attrs: dict, **kwargs) -> dict:
        """Return the status dictionary for this UDI event."""
        status = {
            "timestamp": self.TimeStamp(),
            "user": os.environ.get("USER", "unknown"),
            **attrs,
            **kwargs,
        }
        return status

    def _track_lineage(self, action, udi: UDI, prefix: str, **kwargs):
        """Store the UDI in the domain."""
        uri = udi.uri
        assert uri and isinstance(uri, str)
        # TODO: store hash and other udi attributes
        opts = self._status(udi.attrs, **kwargs)
        logging.debug(f"Domain._track_lineage: {action} {udi} {opts}")
        self.data_yaml.set(prefix, uri, action, opts)
        self.data_yaml.save()
        return True
