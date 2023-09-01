import logging
from urllib.parse import parse_qs, urlparse

from upath import UPath

from .factory import quilt
from .udg.folder import Folder
from .udg.node import Node


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
    def GetQuery(cls, uri: str, key: str) -> str:
        """Extract key from URI query string."""
        query = urlparse(uri).query
        if not query:
            return ""
        qs = parse_qs(query)
        vlist = qs.get(key)
        return vlist[0] if vlist else ""

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        self.store = self.ToPath(self.parent_name(), name)
        logging.debug(f"Domain.root: {self.store}")
        self.base = self._setup_dir(self.store, "config")
        self.path = self._setup_dir(self.base, "names")
