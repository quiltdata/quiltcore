from .codec import Codec, Dict4, List4
from .keyed import Keyed

from pathlib import Path
from typing import Iterator


class Tabular(Keyed):
    """Abstract base class to wrap pa.Table with a dict-like interface."""

    def __init__(self, path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(**kwargs)
        self.path = path
        self.codec = Codec()

    def names(self) -> list[str]:
        return list(self._cache.keys())

    def get_dict4(self, key: str) -> Dict4:
        raise NotImplementedError

    def relax(self, dest: Path) -> List4:
        raise NotImplementedError

    def _get(self, key: str):
        return self.get_dict4(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())
