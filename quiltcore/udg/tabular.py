import pyarrow as pa  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from pathlib import Path
from pyarrow.parquet import ParquetFile
from typing import Iterator

from .codec import Codec, asdict
from .keyed import Keyed
from .types import Dict4, List4


class Tabular(Keyed):
    """Abstract base class to wrap pa.Table with a dict-like interface."""

    EXT4 = ".parquet"
    REL_PATH = "./"

    @staticmethod
    def Write4(list4: List4, path: Path):
        """Write a list4 to a parquet file."""
        dicts = [asdict(dict4) for dict4 in list4]
        table = pa.Table.from_pylist(dicts)
        pq.write_table(table, path.with_suffix(Tabular.EXT4))

    @staticmethod
    def Read4(path: Path) -> pa.Table:
        """Read a parquet file into a pa.Table."""
        with path.open(mode="rb") as fi:
            return ParquetFile(fi).read()

    def __init__(self, path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(**kwargs)
        self.path = path
        self.codec = Codec()
        self.prefix = self.REL_PATH

    def first(self, table) -> dict:
        return table.take([0]).to_pylist()[0]

    def _relax(self, row: Dict4, dest: Path) -> Dict4:
        if row.name == ".":
            return row
        place = row.place.replace(self.REL_PATH, self.REL_PATH + self.prefix)
        path = self.codec.AsPath(place)
        assert path.exists(), f"_relax: source[{place}] not found at {path}"
        with path.open("rb") as fi:
            dest.write_bytes(fi.read())
        row.place = self.codec.AsStr(dest)
        return row

    def relax(self, dest_dir: Path, prefix: str = "") -> List4:
        assert dest_dir.exists() and dest_dir.is_dir()
        self.prefix = prefix if prefix[-1] == "/" else prefix + "/"
        return [self._relax(r, dest_dir / n) for n, r in self.items()]

    def names(self) -> list[str]:
        return list(self._cache.keys())

    def get_dict4(self, key: str) -> Dict4:
        raise NotImplementedError

    def _get(self, key: str):
        return self.get_dict4(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())
