from .udg.child import Child
from .factory import quilt

class Domain(Child):

    URI_SPLIT = '://'

    @classmethod
    def FromURI(cls, uri):
        scheme, path = uri.split(cls.URI_SPLIT)
        return quilt[scheme][path]
