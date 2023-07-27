from datetime import datetime
from pathlib import Path

import pyarrow as pa  # type: ignore

from .resource_key import ResourceKey


class Header(ResourceKey):
    """
    Represents a single row in a Manifest.
    Attributes:

    * name: str (logical_key)
    * path: Path (physical_key)
    * size: int
    * hash: str[multihash]
    * metadata: object

    """

    def __init__(self, path: Path, **kwargs):
        super().__init__(path, **kwargs)
        self.cols: list[str] = []
        self._setup_headers(kwargs["first"])

    #
    # Setup
    #

    def _setup_headers(self, first: dict):
        for header, default in self.headers.items():
            value = first.get(header, default)
            setattr(self, header, value)
            if header in first:
                self.cols.append(header)

    def drop(self, table) -> pa.Table:
        return table.drop(self.cols).slice(1)

    #
    # Output
    #

    def to_dict(self) -> dict:
        raw_dict = {k: getattr(self, k) for k in self.headers.keys()}
        return self.codec.encode_dates(raw_dict)

    def to_hashable(self) -> dict:
        meta = self.to_dict()
        if hasattr(self, self.KEY_USER):
            user_meta = getattr(self, self.KEY_USER)
            for k, v in user_meta.items():
                if isinstance(v, datetime):
                    user_meta[k] = self.codec.encode_date(v)
            meta[self.KEY_USER] = user_meta
        return meta
