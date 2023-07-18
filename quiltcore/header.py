import logging
from datetime import datetime
from pathlib import Path

import pyarrow as pa  # type: ignore

from .resource import Resource
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
        self._setup(kwargs['first'])

    #
    # Setup
    #

    def header_keys(self) -> list[str]:
        headers = self.cf.get_dict("quilt3/headers")
        return list(headers.keys())

    def _setup(self, first: dict):
        for header in self.header_keys():
            if header in first:
                self.cols.append(header)
                value = self.RowValue(first, header)
                setattr(self, header, value)

    def drop(self, table) -> pa.Table:
        return table.drop(self.cols).slice(1)
    
    #
    # Output
    #

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.cols}

    def to_hashable(self) -> dict:
        meta = self.to_dict()
        print(f"meta: {meta}")
        user_meta = getattr(self, self.kMeta) if hasattr(self, self.kMeta) else None
        if not user_meta:
            user_meta = {}
        print(f"user_meta: {user_meta}")
        for k, v in user_meta.items():
            if isinstance(v, datetime):
                fmt = self.cf.get_str("quilt3/format/datetime", "%Y-%m-%d")
                user_meta[k] = v.strftime(fmt)
        meta[self.kMeta] = user_meta
        return meta



        