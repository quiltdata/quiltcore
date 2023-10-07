from pathlib import Path
from typing import Iterator

from .codec import Codec, Dict4, List4
from .keyed import Keyed


class Tabular(Keyed):
    """Abstract base class to wrap pa.Table with a dict-like interface."""

    def __init__(self, path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(**kwargs)
        self.path = path
        self.codec = Codec()

    def first(self, table) -> dict:
        return table.take([0]).to_pylist()[0]

    def _relax(self, row: Dict4, dest: Path) -> Dict4:
        if row.name == ".":
            return row
        path = self.codec.AsPath(row.place)
        with path.open("rb") as fi:
            dest.write_bytes(fi.read())
        row.place = self.codec.AsStr(dest)
        return row

    def relax(self, dest_dir: Path) -> List4:
        assert dest_dir.exists() and dest_dir.is_dir()
        return [self._relax(r, dest_dir / n) for n, r in self.items()]

    def names(self) -> list[str]:
        return list(self._cache.keys())

    def get_dict4(self, key: str) -> Dict4:
        raise NotImplementedError

    def _get(self, key: str):
        return self.get_dict4(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())
