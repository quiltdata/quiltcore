from .codec import Dict3, Dict4
from .keyed import Keyed

from pathlib import Path
from typing import Iterator


class Tabular(Keyed):
    """Abstract base class to wrap pa.Table with a dict-like interface."""

    def names(self) -> list[str]:
        return list(self._cache.keys())

    def get_dict3(self, key: str) -> Dict3:
        raise NotImplementedError

    def get_dict4(self, key: str) -> Dict4:
        raise NotImplementedError
 
    def relax(self, dest: Path) -> list[Dict4]:
        raise NotImplementedError

    def _get(self, key: str):
        return self.get_dict4(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())
