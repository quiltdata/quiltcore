import logging

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

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        self.store = self.ToPath(self.parent_name(), name)
        logging.debug(f"Domain.root: {self.store}")
        self.base = self._setup_dir(self.store, "config")
        self.path = self._setup_dir(self.base, "names")
        self.remotes = self._setup_dir(self.base, "remotes")
        self.is_mutable = kwargs.get(self.K_MUTABLE, False)
        self.data_yaml = Data(self.store)

    
    def pull(self, udi: UDI):
        self.data_yaml.save()
        return True
