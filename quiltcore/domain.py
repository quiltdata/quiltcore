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
    def ToURI(cls, scheme, domain):
        if scheme == "file":
            domain = domain.replace("\\", "/")
            return domain
        uri = f"{scheme}{cls.URI_SPLIT}{domain}"
        return uri
    
    @classmethod
    def ToPath(cls, scheme, domain):
        uri = cls.ToURI(scheme, domain)
        logging.debug(f"Domain.ToPath: {uri}")
        return UPath(uri)

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        self.root = self.ToPath(self.parent_name(), name)
        logging.debug(f"Domain.root: {self.root}")
        self.base = self._setup_dir(self.root, "config")
        self.path = self._setup_dir(self.base, "names")
