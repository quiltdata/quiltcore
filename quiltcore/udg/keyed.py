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
        self._cache = {}
        self.set_dirty(False)

    def _get(self, key: str):
        raise KeyError(key)

    def set_dirty(self, state: bool = True):
        self.__dirty = True

    def is_dirty(self) -> bool:
        return self.__dirty

    def __getitem__(self, key: str):
        result = self._cache.get(key, None)
        if result is None:
            result = self._get(key)
            self._cache[key] = result
        return result

    def __iter__(self) -> Iterator[str]:
        return iter(self._cache)

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def __setitem__(self, key, value):
        self._cache[key] = value
        self.set_dirty()

    def __delitem__(self, key):
        del self._cache[key]
        self.set_dirty()
