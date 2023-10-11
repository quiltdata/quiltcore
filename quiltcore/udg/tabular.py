import logging  # noqa: F401

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
    def Write4(list4: List4, path: Path) -> Path:
        """Write a list4 to a parquet file."""
        parquet_path = path.with_suffix(Tabular.EXT4)
        dicts = [asdict(dict4) for dict4 in list4]
        table = pa.Table.from_pylist(dicts)
        pq.write_table(table, parquet_path)
        return parquet_path

    @staticmethod
    def Read4(path: Path) -> pa.Table:
        """Read a parquet file into a pa.Table."""
        with path.open(mode="rb") as fi:
            return ParquetFile(fi).read()

    @staticmethod
    def FindTablePath(path: Path) -> Path:
        """Find parquet or normal hash."""
        parquet_path = path.with_suffix(Tabular.EXT4)
        return parquet_path if parquet_path.exists() else path

    #
    # Initialization
    #

    def __init__(self, path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(**kwargs)
        self.path = path
        self.codec = Codec()
        self.base = self.path.parent.parent.parent
        self.table = self._get_table()
        self.head = self._get_head()
        self.body = self._get_body()
        logging.debug(f"Tabular.__init__: {self.base} <- {self.path}")

    #
    # Parse Table
    #

    def first(self) -> dict:
        header = self.table.take([0])
        return header.to_pylist()[0]

    def _get_table(self) -> pa.Table:
        raise NotImplementedError

    def _get_head(self) -> pa.Table:
        """Extract header values into attributes."""
        raise NotImplementedError

    def _get_body(self) -> pa.Table:
        """
        Extract header values into attributes.
        Return the Table without header row and columns
        """
        raise NotImplementedError

    #
    # Accessors
    #

    def names(self) -> list[str]:
        return list(self._cache.keys())

    def get_dict4(self, key: str) -> Dict4:
        raise NotImplementedError

    def _get(self, key: str):
        return self.get_dict4(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.names())

    #
    # Converters
    #

    def as_path(self, place: str) -> Path:
        assert isinstance(place, str)
        assert len(place) > 1
        match place[0]:
            case ".":
                return self.base / place[2:]
            case "/":
                return Path(place)
            case _:
                return self.codec.AsPath(place)

    def as_place(self, path: Path) -> str:
        if self.base in path.parents:
            path = path.relative_to(self.base)
        return self.codec.AsStr(path)

    # Relaxation

    def _relax(self, row: Dict4, install_path: Path) -> Dict4:
        if row.name == ".":
            return row
        path = self.as_path(row.place)
        assert path.exists(), f"_relax: {path} not found for {row}"
        with path.open("rb") as fi:
            install_path.write_bytes(fi.read())
        row.place = self.as_place(install_path)
        return row

    def relax(self, install_dir: Path, prefix: str = "") -> List4:
        assert install_dir.exists() and install_dir.is_dir()
        return [self._relax(row, install_dir / name) for name, row in self.items()]
