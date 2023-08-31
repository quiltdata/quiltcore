import logging

from .factory import quilt
from .udg.folder import Folder

from upath import UPath

class Domain(Folder):
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

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        self.store = self.ToPath(self.parent_name(), name)
        logging.debug(f"Domain.root: {self.store}")
        self.base = self._setup_dir(self.store, "config")
        self.path = self._setup_dir(self.base, "names")
