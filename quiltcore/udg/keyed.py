"""A Mapping is a generic container for associating key/value
pairs.

This class provides concrete generic implementations of all
methods except for __getitem__, __iter__, and __len__.

"""

from collections.abc import MutableMapping

from .root import Root


class Keyed(Root, MutableMapping):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}

    def __getitem__(self, key):
        return self.cache.get(key, None)

    def __iter__(self):
        return iter(self.cache)

    def __len__(self):
        return len(self.cache)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __delitem__(self, key):
        del self.cache[key]
