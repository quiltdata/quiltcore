from .factory import quilt
from .udg.child import Child

from upath import UPath

class Domain(Child):
    URI_SPLIT = "://"

    @classmethod
    def FromURI(cls, uri):
        scheme, path = uri.split(cls.URI_SPLIT)
        return quilt[scheme][path]
    
    @classmethod
    def ToPath(cls, scheme, domain):
        uri = f"{scheme}{cls.URI_SPLIT}{domain}"
        print(f"Domain.ToURI: {scheme}, {domain} -> {uri}")
        return UPath(uri)

    def __init__(self, name, parent, **kwargs):
        super().__init__(name, parent, **kwargs)
        print(f"Domain.init: {self} <- {parent}")
        print(f"Domain.self.parent[{self.parent_name()}]: {self.parent}")
        self.path = self.ToPath(self.parent_name(), name)