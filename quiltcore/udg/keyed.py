"""A Mapping is a generic container for associating key/value
pairs.

This class provides concrete generic implementations of all
methods except for __getitem__, __iter__, and __len__.

"""

from collections.abc import MutableMapping
from typing import Iterator

from .root import Root


class Keyed(Root, MutableMapping):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}

    def _get(self, key: str):
        raise KeyError(key)

    def __getitem__(self, key: str):
        result = self.cache.get(key, None)
        if result is None:
            result = self._get(key)
            self.cache[key] = result
        return result

    def __iter__(self) -> Iterator[str]:
        return iter(self.cache)

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __delitem__(self, key):
        del self.cache[key]

