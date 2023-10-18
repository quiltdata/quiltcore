import logging  # noqa: F401
import json

import pyarrow as pa  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from pathlib import Path
from pyarrow.parquet import ParquetFile
from typing import Iterator

from .codec import Codec
from .keyed import Keyed
from .types import Dict4, List4, Types
from .verifiable import Verifiable


class Tabular(Keyed):
    """Abstract base class to wrap pa.Table with a dict-like interface."""

    EXT4 = ".parquet"
    REL_PATH = "./"

    @staticmethod
    def Write4(list4: List4, path: Path) -> Path:
        """Write a list4 to a parquet file."""
        parquet_path = path.with_suffix(Tabular.EXT4)
        dicts = [dict4.to_parquet_dict() for dict4 in list4]
        table = pa.Table.from_pylist(dicts)
        pq.write_table(table, parquet_path)
        return parquet_path

    @staticmethod
    def UnparseTable(table: pa.Table) -> pa.Table:
        """Unaparse K_METADATA column."""
        json_col = table.column(Types.K_META_JSON)
        table = table.append_column(
            Types.K_METADATA,
            pa.array([json.loads(x.as_py()) for x in json_col]),
        )
        table = table.remove_column(table.num_columns - 2)
        return table

    @staticmethod
    def Read4(path: Path) -> pa.Table:
        """Read a parquet file into a pa.Table."""
        with path.open(mode="rb") as fi:
            table = ParquetFile(fi).read()
            return Tabular.UnparseTable(table)

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"

    def __str__(self) -> str:
        return self.table.__str__()

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
        """Convert a place string into a Path."""
        assert isinstance(place, str)
        assert len(place) > 1
        match place[0]:
            case self.HEADER_NAME:
                return self.base / place[2:]
            case "/":
                return Path(place)
            case _:
                return self.codec.AsPath(place)

    def as_place(self, path: Path) -> str:
        """Convert a Path back into a place string."""
        path = self.codec.RelativePath(path, self.base)
        return self.codec.AsString(path)

    # Relaxation

    def relax(self, install_dir: Path) -> List4:
        """Relax each row of this remote Table into local install_dir."""
        assert install_dir.exists() and install_dir.is_dir()
        return [self._relax(row, install_dir / name) for name, row in self.items()]

    def _relax(self, row: Dict4, install_path: Path) -> Dict4:
        """Relax remote_path of each row into local install_path."""
        if row.name == self.HEADER_NAME:
            return row
        remote_path = self.as_path(row.place)
        assert remote_path.exists(), f"_relax: {remote_path} not found for {row.place}"
        with remote_path.open("rb") as fi:
            install_path.write_bytes(fi.read())
        return Verifiable.UpdateDict4(row, install_path)
