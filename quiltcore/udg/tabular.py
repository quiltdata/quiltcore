import logging  # noqa: F401
import json

import pyarrow as pa  # type: ignore
import pyarrow.parquet as pq  # type: ignore

from pathlib import Path
from pyarrow.parquet import ParquetFile
from typing import Iterator

from .codec import Codec
from .header import Header
from .keyed import Keyed
from .types import Dict3, Dict4, List4, Types
from .verifiable import Verifiable

from jsonlines import Writer  # type: ignore


class Tabular(Keyed):
    """
    Abstract base class to wrap pa.Table as a series of Dict4 dataclasses.

    * Represents both JSON and Parquet as Dict4
    * Simulates Header as another Dict4 row with name `HEADER_NAME="."`
    * Where `version` and `message` are in `info`, and `user_meta` is in `meta`
    """

    EXT4 = ".parquet"
    REL_PATH = "./"

    @classmethod
    def FindTablePath(cls, path: Path) -> Path:
        """Find parquet or normal hash."""
        parquet_path = cls.ParquetPath(path)
        return parquet_path if parquet_path.exists() else path

    @classmethod
    def ParquetPath(cls, path: Path) -> Path:
        """Convert quilt3 manifest path to parquet path"""
        filename = cls.MULTIHASH + path.name
        return path.with_name(filename).with_suffix(cls.EXT4)

    @classmethod
    def ParquetHash(cls, hash: str) -> str:
        """Convert hash string to parquet filename"""
        path = cls.ParquetPath(Path(hash))
        return path.name

    @classmethod
    def ReadParquet(cls, path: Path) -> pa.Table:
        """Read a parquet file into a pa.Table."""
        with path.open(mode="rb") as fi:
            table = ParquetFile(fi).read()
            return cls.UnparseTable(table)

    @classmethod
    def WriteJSON(cls, head3: dict, rows: list[Dict3], path: Path) -> None:
        """Write manifest contents to _path_"""
        logging.debug(f"Write3: {path}")
        with path.open(mode="wb") as fo:
            with Writer(fo) as writer:
                head3[cls.K_VERSION] = cls.HEADER_V3
                writer.write(head3)
                for row in rows:
                    logging.debug(f"WriteJSON: {row}")
                    if not isinstance(row, Dict3):
                        raise ValueError(f"WriteJSON.not_Dict3: {row}")
                    json_dict = row.to_dict()
                    if json_dict:
                        writer.write(json_dict)
                    else:
                        logging.error(f"WriteJSON.missing_dict: {row}")

    @classmethod
    def WriteParquet(cls, list4: List4, path: Path) -> Path:
        """Write a list4 to a parquet file."""
        parquet_path = cls.ParquetPath(path)
        list4[0].info[cls.K_VERSION] = cls.HEADER_V4
        dicts = [dict4.to_parquet_dict() for dict4 in list4]
        table = pa.Table.from_pylist(dicts)
        pq.write_table(table, parquet_path)
        return parquet_path

    @staticmethod
    def ParseColumn(table: pa.Table, field: str) -> pa.Table:
        """Parse JSON column."""
        json_field = f"{field}.json"
        col_id = table.schema.get_field_index(json_field)
        if col_id < 0:
            return table

        json_col = table.column(json_field)
        table = table.append_column(
            field,
            pa.array([json.loads(x.as_py()) for x in json_col]),
        )
        return table.remove_column(col_id)

    @staticmethod
    def UnparseTable(table: pa.Table) -> pa.Table:
        """Parse all JSON_FIELDS column."""
        for field in Types.K_JSON_FIELDS:
            table = Tabular.ParseColumn(table, field)
        return table

    #
    # Initialization
    #

    def __init__(self, path: Path, **kwargs):
        """Read the manifest into a pyarrow Table."""
        super().__init__(**kwargs)
        self.path = path
        self.codec = Codec()
        self.store = self.path.parent.parent.parent
        self.table = self._get_table()
        self.header: Header | None = None
        self.head = self._get_head()
        self.body = self._get_body()
        logging.debug(f"Tabular.__init__: {self.store} <- {self.path}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"

    def __str__(self) -> str:
        return str(self.table)

    #
    # Parse Table
    #

    def first(self) -> dict:
        heading = self.table.take([0])
        assert heading, f"No heading found for {self.path}:\n${self.table}"
        return heading.to_pylist()[0]

    def _get_table(self) -> pa.Table:
        raise NotImplementedError

    def _get_head(self) -> Dict4:
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
        logging.debug(f"as_path: {place}")
        assert isinstance(place, str)
        assert len(place) > 1
        match place[0]:
            case self.HEADER_NAME:
                return self.store / place[2:]
            case "/":
                return Path(place)
            case _:
                if "://" in place:
                    return self.codec.AsPath(place)
        raise ValueError(f"as_path: {place}")

    def as_place(self, path: Path) -> str:
        """Convert a Path back into a place string."""
        path = self.codec.RelativePath(path, self.store)
        return self.codec.AsString(path)

    # Relaxation

    def relax(self, install_dir: Path, source_dir: Path | None = None) -> List4:
        """Relax each row of this remote Table into local install_dir."""
        install_dir.mkdir(parents=True, exist_ok=True)
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
