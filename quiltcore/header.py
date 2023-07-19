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
            value = self.RowValue(first, header, default)
            setattr(self, header, value)
            if header in first:
                self.cols.append(header)

    def drop(self, table) -> pa.Table:
        return table.drop(self.cols).slice(1)

    #
    # Output
    #

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.cols}

    def to_hashable(self) -> dict:
        meta = self.to_dict()
        user_meta = getattr(self, self.kMeta) if hasattr(self, self.kMeta) else None
        if not user_meta:
            user_meta = {}
        for k, v in user_meta.items():
            if isinstance(v, datetime):
                fmt = self.cf.get_str("quilt3/format/datetime", "%Y-%m-%d")
                user_meta[k] = v.strftime(fmt)
        meta[self.kMeta] = user_meta
        return meta
